#!/usr/bin/env python3
"""
Metro Trade - Trueque en el Metro
Flask 后端：地铁线商品、用户发布、埋点统计，无图书相关功能。
"""

from flask import Flask, render_template, jsonify, request, send_from_directory, send_file, Response
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import random
from pathlib import Path
from typing import Optional, Dict, Any
from collections import defaultdict
from threading import Lock

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# =========================
# 地铁交易供给数据（从 static/data/products.json 加载）
# =========================

METRO_PRODUCTS = []
# 顺序：Todos, Línea 1..9, Línea A, Línea B, Línea 12（LA/LB 在 L9 与 L12 之间）
METRO_LINES = ["all", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "12"]

# 用户发布的商品（内存存储，与 JSON 供给合并展示）
_user_products = []
_user_products_lock = Lock()
_user_product_id = 10000


def load_metro_products():
    """加载供给列表：metro_products.json（或 products.json），再追加清洗后的 Facebook 商品 facebook_products.json"""
    global METRO_PRODUCTS
    app_root = Path(__file__).resolve().parent
    METRO_PRODUCTS = []
    for json_path in (app_root / "metro_products.json", app_root / "static" / "data" / "products.json"):
        try:
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    METRO_PRODUCTS = data.get("products", [])
                    print(f"✅ Cargados {len(METRO_PRODUCTS)} productos de metro desde {json_path.name}")
                    break
        except Exception as e:
            print(f"⚠️ Error leyendo {json_path.name}: {e}")
    else:
        print("⚠️ No se encontró metro_products.json ni static/data/products.json")
    # 追加清洗后的 Facebook 帖子商品（可直接展示）
    fb_path = app_root / "static" / "data" / "facebook_products.json"
    try:
        if fb_path.exists():
            with open(fb_path, "r", encoding="utf-8") as f:
                fb_data = json.load(f)
            fb_list = fb_data.get("products", [])
            METRO_PRODUCTS = METRO_PRODUCTS + fb_list
            print(f"✅ Añadidos {len(fb_list)} productos de Facebook (facebook_products.json)")
    except Exception as e:
        print(f"⚠️ Error leyendo facebook_products.json: {e}")


def _product_matches_metro(p, metro):
    """商品是否在该线路展示：含该线路 或 含 all（all 表示每条线都展示）"""
    lines = p.get("metro_lines") or []
    if metro == "all" or not metro:
        return True
    return metro in lines or "all" in lines


def _product_sort_key(p):
    """排序键：全线路（含 all）的排后面，其余排前面。"""
    lines = p.get("metro_lines") or []
    return (1 if "all" in lines else 0)


def _is_valid_product_image(img):
    """图片有效才展示：非空且为合法 base64 data URL 或有效 URL。无效则屏蔽该商品。"""
    if not img or not str(img).strip():
        return False
    s = str(img).strip()
    if s.startswith('data:image') and len(s) > 50:
        return True
    if s.startswith('http://') or s.startswith('https://') or s.startswith('/'):
        return True
    return False


def _is_fake_price(price):
    """free、0、1、2 比索视为明显假价格，需屏蔽或发布前提示。"""
    if price is None:
        return True
    p = str(price).strip().lower()
    if not p or p in ('0', '1', '2', 'free', 'gratis', 'gratis.', '0.00', '1.00', '2.00'):
        return True
    # 仅数字且为 1 或 2
    try:
        n = float(p.replace(',', '.'))
        if 0 <= n <= 2:
            return True
    except ValueError:
        pass
    return False


def get_products_by_metro(metro):
    """按地铁线过滤商品。用户上传的排前面，供给在后。隐藏：假价格、已封禁、图片无效（裂图）。"""
    base = list(METRO_PRODUCTS)
    user_list = list_metro_user_products(limit=500)
    user_copies = [dict(p, _from_user=True) for p in user_list]
    base_copies = [dict(p, _from_user=False) for p in base]
    combined = user_copies + base_copies
    if not metro or metro == "all":
        filtered = combined
    else:
        filtered = [p for p in combined if _product_matches_metro(p, metro)]
    # 屏蔽假价格、已封禁、图片无效（裂图不展示）
    filtered = [
        p for p in filtered
        if not p.get('banned')
        and not _is_fake_price(p.get('price'))
        and _is_valid_product_image(p.get('image'))
    ]
    user_part = sorted([p for p in filtered if p.get('_from_user')], key=_product_sort_key)
    supply_part = sorted([p for p in filtered if not p.get('_from_user')], key=_product_sort_key)
    out = user_part + supply_part
    for p in out:
        p.pop('_from_user', None)
    return out


# 启动时加载（首次请求前也会在路由里确保已加载）
load_metro_products()

# =========================
# 简单埋点 & 统计存储（支持数据库持久化 + 内存回退）
# =========================

import json
from collections import defaultdict
from threading import Lock

# 检测是否配置了数据库
_use_database = False
_db_conn = None

def _init_database_if_available():
    """尝试初始化数据库连接（如果配置了环境变量），并创建所需表结构"""
    global _use_database, _db_conn
    try:
        database_url = (os.environ.get('DATABASE_URL') or 
                       os.environ.get('POSTGRES_URL') or 
                       os.environ.get('NEON_DATABASE_URL') or
                       os.environ.get('SUPABASE_DATABASE_URL'))
        
        if database_url:
            import psycopg2
            # Vercel/Neon 提供的 URL 格式转换
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            # Neon 冷启动需几秒，拉长连接超时避免 serverless 下首次连失败
            if 'connect_timeout' not in database_url:
                database_url += '&connect_timeout=5' if '?' in database_url else '?connect_timeout=5'
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # 埋点事件表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS book_exchange_events (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(50) NOT NULL,
                    book_id INTEGER,
                    anon_id TEXT,
                    extra JSONB,
                    ip VARCHAR(45),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON book_exchange_events(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON book_exchange_events(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_book_id ON book_exchange_events(book_id)')

            # 线上图书集市（Tianguis）列表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS book_market_items (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    whatsapp TEXT NOT NULL,
                    city TEXT,
                    image TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_created_at ON book_market_items(created_at DESC)')

            # 地铁用户发布商品（持久化后前台可稳定展示）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metro_user_products (
                    id SERIAL PRIMARY KEY,
                    metro_lines JSONB NOT NULL,
                    price TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    image TEXT,
                    contact_link TEXT,
                    contact_link_2 TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metro_user_products_created_at ON metro_user_products(created_at DESC)')
            try:
                cursor.execute('ALTER TABLE metro_user_products ADD COLUMN banned BOOLEAN DEFAULT FALSE')
            except Exception:
                pass
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS product_reports (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_reports_product_id ON product_reports(product_id)')
            
            conn.commit()
            cursor.close()
            _db_conn = conn
            _use_database = True
            print('✅ 数据库连接成功，使用持久化存储')
            return True
    except ImportError:
        print('⚠️ psycopg2 未安装，使用内存存储')
    except Exception as e:
        print(f'⚠️ 数据库连接失败，使用内存存储: {e}')
    
    _use_database = False
    return False

# 尝试初始化数据库
_init_database_if_available()

# 内存存储（作为回退方案）
_analytics_storage = {
    'events': [],  # 存储所有事件
    'lock': Lock()  # 线程锁
}

# 图书集市内存存储（用于数据库不可用时的回退）
_market_storage = {
    'items': [],
    'lock': Lock()
}

def get_analytics_storage():
    """获取分析存储（内存）"""
    return _analytics_storage


def get_market_storage():
    """获取图书集市存储（内存回退用）"""
    return _market_storage


def create_market_item(title: str, description: str, whatsapp: str, city: Optional[str] = None,
                      image: Optional[str] = None) -> Dict[str, Any]:
    """创建一条图书集市记录（优先写入数据库，失败则写入内存）"""
    item = {
        'id': None,
        'title': title.strip(),
        'description': description.strip(),
        'whatsapp': whatsapp.strip(),
        'city': (city or '').strip(),
        'image': (image or '').strip() if image else '',
        'created_at': datetime.utcnow().isoformat()
    }

    # 优先使用数据库
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            cursor.execute(
                '''
                INSERT INTO book_market_items (title, description, whatsapp, city, image)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, image, created_at
                ''',
                (item['title'], item['description'], item['whatsapp'], item['city'] or None, item['image'] or None)
            )
            row = cursor.fetchone()
            if row:
                item['id'] = row[0]
                item['image'] = row[1] or ''
                if row[2]:
                    item['created_at'] = row[2].isoformat() if hasattr(row[2], 'isoformat') else str(row[2])
            cursor.close()
            return item
        except Exception as e:
            print(f'⚠️ 图书集市写入数据库失败，将写入内存: {e}')

    # 回退到内存
    storage = get_market_storage()
    with storage['lock']:
        item['id'] = len(storage['items']) + 1
        storage['items'].append(item)
        # 限制长度，避免内存无限增长
        if len(storage['items']) > 1000:
            storage['items'] = storage['items'][-1000:]
    return item


def list_market_items(limit: int = 100) -> list:
    """获取图书集市最近的条目列表（优先从数据库）"""
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            cursor.execute(
                '''
                SELECT id, title, description, whatsapp, city, image, created_at
                FROM book_market_items
                ORDER BY created_at DESC
                LIMIT %s
                ''',
                (limit,)
            )
            rows = cursor.fetchall()
            cursor.close()
            items = []
            for row in rows:
                items.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'whatsapp': row[3],
                    'city': row[4] or '',
                    'image': row[5] or '',
                    'created_at': row[6].isoformat() if hasattr(row[6], 'isoformat') else str(row[6])
                })
            return items
        except Exception as e:
            print(f'⚠️ 图书集市读取数据库失败，回退到内存: {e}')

    storage = get_market_storage()
    with storage['lock']:
        # 内存中已按插入顺序，取最近的 limit 条，按时间倒序返回
        items = list(storage['items'])[-limit:]
        items.reverse()
        return items


def list_metro_user_products(limit: int = 100, include_banned: bool = False) -> list:
    """获取地铁用户发布商品列表（优先从数据库，最新在前）。默认排除已封禁。"""
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            if include_banned:
                cursor.execute(
                    '''
                    SELECT id, metro_lines, price, title, description, image, contact_link, contact_link_2, created_at, COALESCE(banned, false)
                    FROM metro_user_products
                    ORDER BY created_at DESC
                    LIMIT %s
                    ''',
                    (limit,)
                )
            else:
                cursor.execute(
                    '''
                    SELECT id, metro_lines, price, title, description, image, contact_link, contact_link_2, created_at, COALESCE(banned, false)
                    FROM metro_user_products
                    WHERE COALESCE(banned, false) = false
                    ORDER BY created_at DESC
                    LIMIT %s
                    ''',
                    (limit,)
                )
            rows = cursor.fetchall()
            cursor.close()
            out = []
            for row in rows:
                lines = row[1]
                if isinstance(lines, str):
                    try:
                        lines = json.loads(lines) if lines else []
                    except Exception:
                        lines = []
                out.append({
                    'id': row[0],
                    'metro_lines': lines or [],
                    'price': row[2] or '0',
                    'title': row[3] or '',
                    'description': row[4] or '',
                    'image': row[5] or '',
                    'contact_link': row[6] or '#',
                    'contact_link_2': row[7] or '#',
                    'created_at': row[8].isoformat() if hasattr(row[8], 'isoformat') else str(row[8]),
                    'banned': row[9] if len(row) > 9 else False,
                })
            return out
        except Exception as e:
            print(f'⚠️ 地铁用户商品读取数据库失败: {e}')

    with _user_products_lock:
        items = list(_user_products)[-limit:]
        items.reverse()
        return [dict(x) for x in items]


def ban_product_by_id(product_id: int) -> bool:
    """封禁商品（设置 banned=true），举报审核通过后调用。"""
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            cursor.execute('UPDATE metro_user_products SET banned = true WHERE id = %s', (product_id,))
            n = cursor.rowcount
            cursor.close()
            return n > 0
        except Exception as e:
            print(f'⚠️ 封禁商品失败: {e}')
    return False


def list_product_reports(limit: int = 50) -> list:
    """举报列表（用于后台），含 product_id、reason、created_at。"""
    db_conn = _get_db_connection()
    if not db_conn:
        return []
    try:
        cursor = db_conn.cursor()
        cursor.execute(
            '''
            SELECT r.id, r.product_id, r.reason, r.created_at, p.title, p.price
            FROM product_reports r
            LEFT JOIN metro_user_products p ON p.id = r.product_id
            ORDER BY r.created_at DESC
            LIMIT %s
            ''',
            (limit,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return [
            {
                'id': row[0],
                'product_id': row[1],
                'reason': row[2] or '',
                'created_at': row[3].isoformat() if hasattr(row[3], 'isoformat') else str(row[3]),
                'product_title': row[4] or '',
                'product_price': row[5] or '',
            }
            for row in rows
        ]
    except Exception as e:
        print(f'⚠️ 举报列表读取失败: {e}')
        return []


def create_metro_user_product(metro_lines: list, price: str, title: str, description: str,
                              image: str, contact_link: str) -> Optional[dict]:
    """写入一条地铁用户发布商品（优先数据库）。返回创建的 item 或 None。"""
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            cursor.execute(
                '''
                INSERT INTO metro_user_products (metro_lines, price, title, description, image, contact_link, contact_link_2)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, metro_lines, price, title, description, image, contact_link, contact_link_2, created_at
                ''',
                (json.dumps(metro_lines), price, title, description, (image or '')[:500000], contact_link or '#', contact_link or '#')
            )
            row = cursor.fetchone()
            cursor.close()
            if row:
                lines = row[1]
                if isinstance(lines, str):
                    try:
                        lines = json.loads(lines) if lines else []
                    except Exception:
                        lines = []
                return {
                    'id': row[0],
                    'metro_lines': lines or [],
                    'price': row[2] or '0',
                    'title': row[3] or '',
                    'description': row[4] or '',
                    'image': row[5] or '',
                    'contact_link': row[6] or '#',
                    'contact_link_2': row[7] or '#',
                    'created_at': row[8].isoformat() if hasattr(row[8], 'isoformat') else str(row[8])
                }
        except Exception as e:
            print(f'⚠️ 地铁用户商品写入数据库失败: {e}')
    return None


def _get_db_connection():
    """获取数据库连接（处理 Neon 自动休眠）。若启动时未连上，每次请求先尝试轻量连接，成功即用。"""
    global _db_conn, _use_database
    # 启动时完整 init 可能超时或某条 DDL 失败，这里先只做“连接+SELECT 1”，成功即可读库
    if not _use_database:
        database_url = (os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL') or
                        os.environ.get('NEON_DATABASE_URL') or os.environ.get('SUPABASE_DATABASE_URL'))
        if database_url:
            try:
                import psycopg2
                u = database_url.replace('postgres://', 'postgresql://', 1) if database_url.startswith('postgres://') else database_url
                if 'connect_timeout' not in u:
                    u += '&connect_timeout=5' if '?' in u else '?connect_timeout=5'
                conn = psycopg2.connect(u)
                conn.cursor().execute('SELECT 1')
                _db_conn = conn
                _use_database = True
            except Exception:
                pass
        if not _use_database:
            _init_database_if_available()
    if _use_database:
        if _db_conn:
            try:
                # 检查连接是否有效
                _db_conn.cursor().execute('SELECT 1')
                return _db_conn
            except Exception as e:
                # 连接失效（可能是 Neon 休眠），关闭旧连接
                try:
                    _db_conn.close()
                except:
                    pass
                _db_conn = None
        
        # 重新连接（Neon 会自动唤醒）
        if not _db_conn:
            try:
                database_url = (os.environ.get('DATABASE_URL') or 
                               os.environ.get('POSTGRES_URL') or 
                               os.environ.get('NEON_DATABASE_URL') or
                               os.environ.get('SUPABASE_DATABASE_URL'))
                if database_url:
                    import psycopg2
                    if database_url.startswith('postgres://'):
                        database_url = database_url.replace('postgres://', 'postgresql://', 1)
                    if 'connect_timeout' not in database_url:
                        database_url += '&connect_timeout=5' if '?' in database_url else '?connect_timeout=5'
                    _db_conn = psycopg2.connect(database_url)
                    return _db_conn
            except Exception as e:
                print(f'⚠️ 数据库重连失败: {e}')
                return None
    
    return None

def add_event(event_type: str, book_id: Optional[int] = None, 
              anon_id: Optional[str] = None, extra: Dict = None,
              ip: str = '', user_agent: str = ''):
    """添加事件（优先使用数据库，否则使用内存存储）"""
    # 优先使用数据库
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            extra_json = json.dumps(extra or {}, ensure_ascii=False)
            cursor.execute('''
                INSERT INTO book_exchange_events 
                (event_type, book_id, anon_id, extra, ip, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (event_type, book_id, anon_id, extra_json, ip, user_agent))
            db_conn.commit()
            cursor.close()
            return
        except Exception as e:
            print(f'⚠️ 数据库写入失败，回退到内存存储: {e}')
    
    # 回退到内存存储
    storage = get_analytics_storage()
    with storage['lock']:
        event = {
            'id': len(storage['events']) + 1,
            'event_type': event_type,
            'book_id': book_id,
            'anon_id': anon_id,
            'extra': extra or {},
            'ip': ip,
            'user_agent': user_agent,
            'created_at': datetime.utcnow().isoformat()
        }
        storage['events'].append(event)
        # 限制内存使用：只保留最近 10000 条记录
        if len(storage['events']) > 10000:
            storage['events'] = storage['events'][-10000:]

def get_events(event_type: Optional[str] = None, limit: int = None):
    """获取事件列表（优先从数据库，否则从内存）"""
    # 优先使用数据库
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            query = 'SELECT id, event_type, book_id, anon_id, extra, ip, user_agent, created_at FROM book_exchange_events'
            params = []
            if event_type:
                query += ' WHERE event_type = %s'
                params.append(event_type)
            query += ' ORDER BY created_at DESC'
            if limit:
                query += ' LIMIT %s'
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            events = []
            for row in rows:
                try:
                    extra = json.loads(row[4]) if row[4] else {}
                except:
                    extra = {}
                events.append({
                    'id': row[0],
                    'event_type': row[1],
                    'book_id': row[2],
                    'anon_id': row[3],
                    'extra': extra,
                    'ip': row[5] or '',
                    'user_agent': row[6] or '',
                    'created_at': row[7].isoformat() if hasattr(row[7], 'isoformat') else str(row[7])
                })
            cursor.close()
            return events
        except Exception as e:
            print(f'⚠️ 数据库读取失败，回退到内存存储: {e}')
    
    # 回退到内存存储
    storage = get_analytics_storage()
    with storage['lock']:
        events = storage['events']
        if event_type:
            events = [e for e in events if e['event_type'] == event_type]
        if limit:
            events = events[-limit:]
        return events

def count_events(event_type: str) -> int:
    """统计特定类型事件的数量（优先从数据库，否则从内存）"""
    # 优先使用数据库
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM book_exchange_events WHERE event_type = %s', (event_type,))
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            print(f'⚠️ 数据库统计失败，回退到内存存储: {e}')
    
    # 回退到内存存储
    storage = get_analytics_storage()
    with storage['lock']:
        return sum(1 for e in storage['events'] if e['event_type'] == event_type)


def _count_events_by_date(event_type: str, since_date: str = None, before_date: str = None) -> int:
    """按日期条件统计事件数（since_date 含当日，before_date 不含）。用于翻倍计算。"""
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            query = 'SELECT COUNT(*) FROM book_exchange_events WHERE event_type = %s'
            params = [event_type]
            if since_date:
                query += ' AND DATE(created_at) >= %s'
                params.append(since_date)
            if before_date:
                query += ' AND DATE(created_at) < %s'
                params.append(before_date)
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            print(f'⚠️ 数据库统计失败: {e}')
            return 0
    storage = get_analytics_storage()
    with storage['lock']:
        n = 0
        for e in storage['events']:
            if e['event_type'] != event_type:
                continue
            day = str(e.get('created_at', ''))[:10]
            if since_date and day < since_date:
                continue
            if before_date and day >= before_date:
                continue
            n += 1
        return n


def count_events_doubled_from(event_type: str, double_from_date: str) -> int:
    """3.3（含）及以后翻倍再叠加：返回 3.3 之前的数量 + 3.3 及以后的数量*2。"""
    before = _count_events_by_date(event_type, before_date=double_from_date)
    from_and_after = _count_events_by_date(event_type, since_date=double_from_date)
    return before + 2 * from_and_after

def get_distinct_anon_ids(event_type: str) -> set:
    """（旧）获取独立访客 ID 集合，暂保留以兼容后续升级"""
    storage = get_analytics_storage()
    with storage['lock']:
        anon_ids = set()
        for e in storage['events']:
            if e['event_type'] == event_type and e.get('anon_id'):
                anon_ids.add(e['anon_id'])
        return anon_ids


def get_distinct_ips(event_type: str) -> set:
    """获取独立访客 IP 集合（用于 UV 统计，优先从数据库，否则从内存）"""
    # 优先使用数据库
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            cursor.execute('SELECT DISTINCT ip FROM book_exchange_events WHERE event_type = %s AND ip IS NOT NULL AND ip != %s', (event_type, ''))
            ips = {row[0] for row in cursor.fetchall()}
            cursor.close()
            return ips
        except Exception as e:
            print(f'⚠️ 数据库查询失败，回退到内存存储: {e}')
    
    # 回退到内存存储
    storage = get_analytics_storage()
    with storage['lock']:
        ips = set()
        for e in storage['events']:
            if e['event_type'] == event_type and e.get('ip'):
                ips.add(e['ip'])
        return ips


def get_distinct_ips_since(event_type: str, since_date: str) -> set:
    """获取某日期之后的独立访客 IP 集合（用于按上线日期统计 UV）"""
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            cursor.execute(
                '''
                SELECT DISTINCT ip
                FROM book_exchange_events
                WHERE event_type = %s
                  AND ip IS NOT NULL AND ip != %s
                  AND created_at >= %s
                ''',
                (event_type, '', since_date),
            )
            ips = {row[0] for row in cursor.fetchall()}
            cursor.close()
            return ips
        except Exception as e:
            print(f'⚠️ 数据库查询失败（get_distinct_ips_since）: {e}')

    # 回退到内存存储
    storage = get_analytics_storage()
    with storage['lock']:
        ips = set()
        for e in storage['events']:
            if (
                e['event_type'] == event_type
                and e.get('ip')
                and str(e.get('created_at', ''))[:10] >= since_date
            ):
                ips.add(e['ip'])
        return ips

def get_daily_stats(days: int = 30):
    """获取按天统计的 PV/UV（优先从数据库，否则从内存）"""
    # 优先使用数据库
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            cursor.execute('''
                SELECT DATE(created_at) as day,
                       COUNT(*) as pv,
                       COUNT(DISTINCT ip) as uv
                FROM book_exchange_events
                WHERE event_type = %s
                  AND created_at >= CURRENT_DATE - (%s * INTERVAL '1 day')
                GROUP BY day
                ORDER BY day DESC
                LIMIT %s
            ''', ('page_view', days, days))
            rows = cursor.fetchall()
            result = [{'day': str(row[0]), 'pv': row[1], 'uv': row[2]} for row in rows]
            cursor.close()
            return result
        except Exception as e:
            print(f'⚠️ 数据库查询失败，回退到内存存储: {e}')
    
    # 回退到内存存储
    storage = get_analytics_storage()
    with storage['lock']:
        daily = defaultdict(lambda: {'pv': 0, 'uv': set()})
        for e in storage['events']:
            if e['event_type'] == 'page_view':
                day = e['created_at'][:10]  # YYYY-MM-DD
                daily[day]['pv'] += 1
                if e.get('ip'):
                    daily[day]['uv'].add(e['ip'])
        
        # 转换为列表格式
        result = []
        for day in sorted(daily.keys(), reverse=True)[:days]:
            result.append({
                'day': day,
                'pv': daily[day]['pv'],
                'uv': len(daily[day]['uv'])
            })
        return result

def init_analytics_db() -> None:
    """初始化分析存储（内存版本，无需初始化）"""
    pass


# 内存存储无需初始化，直接使用即可

@app.route('/')
def index():
    """首页 - 地铁交易（西语默认）"""
    if not METRO_PRODUCTS:
        load_metro_products()
    return render_template('metro.html', metro_lines=METRO_LINES)


@app.route('/en')
@app.route('/en/')
def index_en():
    """首页 - 英语版（域名/en）"""
    if not METRO_PRODUCTS:
        load_metro_products()
    return render_template('metro.html', metro_lines=METRO_LINES)


@app.route('/api/products', methods=['GET', 'POST'])
def api_products():
    """GET: 列表按地铁线筛选。POST: 用户发布商品。"""
    if request.method == 'GET':
        if not METRO_PRODUCTS:
            load_metro_products()
        metro = (request.args.get('metro') or 'all').strip()
        products = get_products_by_metro(metro)
        return jsonify({'products': products})

    # POST: 用户发布
    global _user_product_id
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    price = str((data.get('price') or '')).strip() or '0'
    metro_lines = data.get('metro_lines')
    if not isinstance(metro_lines, list) or not metro_lines:
        return jsonify({'success': False, 'error': 'metro_lines required (array)'}), 400
    # 只允许已知线路
    allowed = set(METRO_LINES) - {'all'}
    metro_lines = [str(x).strip() for x in metro_lines if str(x).strip() in allowed]
    if not metro_lines:
        return jsonify({'success': False, 'error': 'Select at least one metro line'}), 400
    image = (data.get('image') or '').strip()
    contact_link = (data.get('contact_link') or '').strip()
    if not title:
        return jsonify({'success': False, 'error': 'title required'}), 400
    if _is_fake_price(price):
        return jsonify({
            'success': False,
            'error': 'No se permiten precios "gratis" o 1-2 pesos (precios irreales). Indica un precio real o "Consultar".',
            'code': 'FAKE_PRICE'
        }), 400
    if not image or not image.startswith('data:image'):
        return jsonify({'success': False, 'error': 'image required (base64 data URL)'}), 400
    if len(image) > 2 * 1024 * 1024:
        return jsonify({'success': False, 'error': 'image too large'}), 400
    item = create_metro_user_product(metro_lines, price, title, description, image[:500000] if image else '', contact_link or '#')
    if item:
        return jsonify({'success': True, 'item': item, 'persisted': True})
    # 无数据库时仅存内存，实例重启后丢失；用户上传必须配置 DATABASE_URL 才能持久化并展示给所有人
    with _user_products_lock:
        _user_product_id += 1
        item = {
            'id': _user_product_id,
            'metro_lines': metro_lines,
            'price': price,
            'title': title,
            'description': description,
            'image': image[:500000] if image else '',
            'contact_link': contact_link or '#',
            'contact_link_2': contact_link or '#',
            'created_at': datetime.utcnow().isoformat(),
        }
        _user_products.append(item)
    return jsonify({'success': True, 'item': item, 'persisted': False})


@app.route('/api/report', methods=['POST'])
def api_report():
    """举报商品。body: product_id, reason（可选）。"""
    data = request.get_json(silent=True) or {}
    product_id = data.get('product_id')
    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'product_id required (number)'}), 400
    reason = (data.get('reason') or '').strip()[:500]
    db_conn = _get_db_connection()
    if not db_conn:
        return jsonify({'success': False, 'error': 'Reportes no disponibles sin base de datos'}), 503
    try:
        cursor = db_conn.cursor()
        cursor.execute(
            'INSERT INTO product_reports (product_id, reason) VALUES (%s, %s)',
            (product_id, reason or None)
        )
        db_conn.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Reporte enviado. Revisaremos y actuaremos si procede.'})
    except Exception as e:
        print(f'⚠️ 举报写入失败: {e}')
        return jsonify({'success': False, 'error': 'Error al enviar el reporte'}), 500


@app.route('/admin/report/approve', methods=['GET', 'POST'])
def admin_report_approve():
    """举报审核通过：封禁该商品并重定向回后台。需 token。"""
    req_token = (request.args.get('token') or request.form.get('token') or '').strip()
    _default = '20260109ForMXG'
    admin_token = (os.environ.get('ADMIN_TOKEN') or _default).strip()
    if not req_token or (req_token != admin_token and req_token != _default):
        return 'Unauthorized', 401
    product_id = request.args.get('product_id') or request.form.get('product_id')
    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return 'product_id required', 400
    if ban_product_by_id(product_id):
        return redirect(f'/admin/stats?token={req_token}&banned={product_id}')
    return redirect(f'/admin/stats?token={req_token}')


@app.route('/api/track', methods=['POST'])
def api_track_event():
    """前端埋点上报接口

    记录：
    - event_type: page_view / share / exchange_request / whatsapp_click 等
    - book_id: 相关图书（可选）
    - anon_id: 前端生成的匿名用户ID，用于 UV 统计
    - extra: 其他JSON数据
    """
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    event_type = (data.get('event_type') or '').strip()

    if not event_type:
        return jsonify({'success': False, 'error': 'event_type is required'}), 400

    book_id = data.get('book_id')
    anon_id = (data.get('anon_id') or '').strip() or None
    extra = data.get('extra') or {}

    # 获取真实 IP（处理代理情况）
    ip = request.headers.get('X-Forwarded-For', '')
    if ip:
        # X-Forwarded-For 可能包含多个 IP，取第一个
        ip = ip.split(',')[0].strip()
    if not ip:
        ip = request.remote_addr or ''
    user_agent = request.headers.get('User-Agent', '')

    # 使用内存存储替代 SQLite
    add_event(
        event_type=event_type,
        book_id=book_id,
        anon_id=anon_id,
        extra=extra,
        ip=ip,
        user_agent=user_agent
    )

    return jsonify({'success': True})


@app.route('/admin/db-check', methods=['GET'])
def admin_db_check():
    """仅管理员：诊断运行时是否有 DATABASE_URL 且能连上 DB（不暴露连接串）"""
    _DEFAULT_ADMIN_TOKEN = '20260109ForMXG'
    admin_token = (os.environ.get('ADMIN_TOKEN') or _DEFAULT_ADMIN_TOKEN).strip()
    req_token = (request.args.get('token') or '').strip()
    if not req_token or (req_token != admin_token and req_token != _DEFAULT_ADMIN_TOKEN):
        return jsonify({'error': 'unauthorized'}), 403
    database_url = (os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL') or
                    os.environ.get('NEON_DATABASE_URL') or os.environ.get('SUPABASE_DATABASE_URL'))
    out = {'env_set': bool(database_url), 'connected': False, 'error': None, '_use_database': _use_database}
    if database_url:
        try:
            import psycopg2
            u = database_url.replace('postgres://', 'postgresql://', 1) if database_url.startswith('postgres://') else database_url
            if 'connect_timeout' not in u:
                u += '&connect_timeout=5' if '?' in u else '?connect_timeout=5'
            conn = psycopg2.connect(u)
            conn.cursor().execute('SELECT 1')
            conn.close()
            out['connected'] = True
        except Exception as e:
            out['error'] = str(e)[:200]
    return jsonify(out)


@app.route('/admin/stats', methods=['GET', 'POST'])
def admin_stats():
    """简单后台：PV/UV 与关键行为统计 + 最近提交明细 + 书籍浏览数据"""
    # 默认后台 token（与文档一致，始终接受此值以便即使 env 异常也能登录）
    _DEFAULT_ADMIN_TOKEN = '20260109ForMXG'
    admin_token = (os.environ.get('ADMIN_TOKEN') or _DEFAULT_ADMIN_TOKEN).strip()
    req_token = (request.args.get('token') or request.form.get('token') or '').strip()
    if not req_token and request.query_string:
        import urllib.parse
        qs = urllib.parse.parse_qs(request.query_string.decode('utf-8'))
        if 'token' in qs and qs['token']:
            req_token = (qs['token'][0] or '').strip()

    if not req_token or (req_token != admin_token and req_token != _DEFAULT_ADMIN_TOKEN):
        from flask import Response
        html_403 = """
        <!DOCTYPE html>
        <html lang="es-MX">
        <head>
            <meta charset="UTF-8">
            <title>Acceso Restringido - Trueque Digital</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: #F5E6D3;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                }
                .login-box {
                    background: white;
                    border-radius: 15px;
                    padding: 40px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    max-width: 400px;
                    width: 90%;
                }
                h1 {
                    color: #2C5F2D;
                    margin-bottom: 20px;
                    text-align: center;
                }
                .error {
                    color: #d32f2f;
                    background: #ffebee;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    font-size: 14px;
                    text-align: center;
                }
                input {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #E8D5B7;
                    border-radius: 8px;
                    font-size: 16px;
                    margin-bottom: 20px;
                    box-sizing: border-box;
                }
                input:focus {
                    outline: none;
                    border-color: #2C5F2D;
                }
                button {
                    width: 100%;
                    padding: 12px;
                    background: #2C5F2D;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: background 0.3s;
                }
                button:hover {
                    background: #4A7C59;
                }
            </style>
        </head>
        <body>
            <div class="login-box">
                <h1>🔒 Acceso Restringido</h1>
                <form method="GET" action="/admin/stats">
                    <input type="password" name="token" placeholder="Ingresa el token de acceso" required autofocus>
                    <button type="submit">Acceder</button>
                </form>
            </div>
        </body>
        </html>
        """
        resp = Response(html_403, status=403, mimetype='text/html')
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        return resp

    # Metro Trade 上线日期，用于过滤老数据（仅展示上线以来的数据）
    METRO_LAUNCH_DATE = '2026-02-27'

    # 按天聚合 PV/UV（最近30天），真实数据，无基准值、无翻倍
    daily_all = get_daily_stats(30)
    daily_real = [row for row in daily_all if row.get('day', '') >= METRO_LAUNCH_DATE]
    total_pv = sum(row.get('pv', 0) for row in daily_real)
    total_uv = sum(row.get('uv', 0) for row in daily_real)
    daily = [{'day': row.get('day', ''), 'pv': row.get('pv', 0), 'uv': row.get('uv', 0)} for row in daily_real]

    # 仅地铁相关真实埋点，无图书相关统计
    stats = {
        'total_pv': total_pv,
        'total_uv': total_uv,
        'metro_favorite_count': count_events('metro_favorite'),
        'metro_contact_click_count': count_events('metro_contact_click'),
        'metro_product_click_count': count_events('metro_product_click'),
        'metro_line_filter_count': count_events('metro_line_filter'),
        'metro_publish_click_count': count_events('metro_publish_click'),
        'metro_publish_success_count': count_events('metro_publish_success'),
        'share_count': count_events('share'),
        'whatsapp_click_count': count_events('whatsapp_click'),
    }

    recent_metro_publishes = list_metro_user_products(limit=20)
    recent_publish_events = get_events('metro_publish_success', limit=50)
    product_reports = list_product_reports(limit=50)
    seeded = request.args.get('seeded') == '1'
    db_configured = _use_database  # 未配置时仅存内存，数据会丢失
    return render_template('admin_stats.html', stats=stats, daily=daily, recent_metro_publishes=recent_metro_publishes, recent_publish_events=recent_publish_events, product_reports=product_reports, token=req_token, seeded=seeded, db_configured=db_configured)

@app.route('/admin/seed-demo-stats', methods=['GET'])
def admin_seed_demo_stats():
    """一键补齐近 30 天演示数据（仅当已配置 DATABASE_URL 时有效）。需 token。"""
    req_token = (request.args.get('token') or '').strip()
    _default = '20260109ForMXG'
    admin_token = (os.environ.get('ADMIN_TOKEN') or _default).strip()
    if not req_token or (req_token != admin_token and req_token != _default):
        return 'Unauthorized', 401
    db_conn = _get_db_connection()
    if not db_conn:
        return '''<html><body><p>未配置 DATABASE_URL，无法持久化。请在 Vercel 项目里设置环境变量 DATABASE_URL（Neon/Postgres 等），然后重新部署。</p>
        <p><a href="/admin/stats?token=''' + req_token + '''">返回统计页</a></p></body></html>''', 200
    try:
        cursor = db_conn.cursor()
        METRO_LAUNCH = '2026-02-27'
        today = datetime.utcnow().date()
        launch = datetime.strptime(METRO_LAUNCH, '%Y-%m-%d').date()
        days_back = min(30, (today - launch).days + 1)
        if days_back <= 0:
            days_back = 30
        inserted = 0
        for i in range(days_back):
            day = today - timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            pv = random.randint(8, 25)
            uv = random.randint(3, min(15, pv))
            ips = ['192.168.1.%d' % (j % 255) for j in range(uv)]
            for j in range(pv):
                ip = ips[j % len(ips)]
                ts = datetime(day.year, day.month, day.day, random.randint(8, 20), random.randint(0, 59), random.randint(0, 59))
                cursor.execute('''
                    INSERT INTO book_exchange_events (event_type, book_id, anon_id, extra, ip, user_agent, created_at)
                    VALUES (%s, NULL, NULL, %s, %s, %s, %s)
                ''', ('page_view', '{}', ip, 'Mozilla/5.0', ts))
                inserted += 1
        for _ in range(random.randint(5, 15)):
            d = random.randint(0, days_back - 1)
            day = today - timedelta(days=d)
            ts = datetime(day.year, day.month, day.day, random.randint(10, 21), random.randint(0, 59), random.randint(0, 59))
            cursor.execute('''INSERT INTO book_exchange_events (event_type, book_id, anon_id, extra, ip, user_agent, created_at)
                VALUES ('metro_favorite', NULL, NULL, %s, %s, %s, %s)''', ('{}', '10.0.0.%d' % random.randint(1, 20), 'Mozilla/5.0', ts))
            inserted += 1
        for _ in range(random.randint(3, 12)):
            d = random.randint(0, days_back - 1)
            day = today - timedelta(days=d)
            ts = datetime(day.year, day.month, day.day, random.randint(10, 20), random.randint(0, 59), random.randint(0, 59))
            cursor.execute('''INSERT INTO book_exchange_events (event_type, book_id, anon_id, extra, ip, user_agent, created_at)
                VALUES ('metro_contact_click', NULL, NULL, %s, %s, %s, %s)''', ('{}', '10.0.0.%d' % random.randint(1, 25), 'Mozilla/5.0', ts))
            inserted += 1
        for _ in range(random.randint(2, 8)):
            d = random.randint(0, days_back - 1)
            day = today - timedelta(days=d)
            ts = datetime(day.year, day.month, day.day, random.randint(9, 19), random.randint(0, 59), random.randint(0, 59))
            cursor.execute('''INSERT INTO book_exchange_events (event_type, book_id, anon_id, extra, ip, user_agent, created_at)
                VALUES ('share', NULL, NULL, %s, %s, %s, %s)''', ('{}', '10.0.0.%d' % random.randint(1, 18), 'Mozilla/5.0', ts))
            inserted += 1
        for _ in range(random.randint(10, 35)):
            d = random.randint(0, days_back - 1)
            day = today - timedelta(days=d)
            ts = datetime(day.year, day.month, day.day, random.randint(8, 22), random.randint(0, 59), random.randint(0, 59))
            cursor.execute('''INSERT INTO book_exchange_events (event_type, book_id, anon_id, extra, ip, user_agent, created_at)
                VALUES ('metro_line_filter', NULL, NULL, %s, %s, %s, %s)''', ('{}', '10.0.0.%d' % random.randint(1, 30), 'Mozilla/5.0', ts))
            inserted += 1
        for _ in range(random.randint(15, 50)):
            d = random.randint(0, days_back - 1)
            day = today - timedelta(days=d)
            ts = datetime(day.year, day.month, day.day, random.randint(9, 21), random.randint(0, 59), random.randint(0, 59))
            cursor.execute('''INSERT INTO book_exchange_events (event_type, book_id, anon_id, extra, ip, user_agent, created_at)
                VALUES ('metro_product_click', NULL, NULL, %s, %s, %s, %s)''', ('{}', '10.0.0.%d' % random.randint(1, 25), 'Mozilla/5.0', ts))
            inserted += 1
        db_conn.commit()
        cursor.close()
        return redirect('/admin/stats?token=%s&seeded=1' % req_token)
    except Exception as e:
        return '<html><body><p>补齐失败: %s</p><a href="/admin/stats?token=%s">返回</a></body></html>' % (str(e), req_token), 200

@app.route('/static/<path:path>')
def send_static(path):
    """提供静态文件"""
    import urllib.parse
    from flask import abort, Response
    import os
    
    # 处理URL编码的路径
    decoded_path = urllib.parse.unquote(path)
    
    # 在Vercel环境下，静态文件可能在多个位置
    # 尝试多个可能的路径
    possible_dirs = [
        Path(app.static_folder or 'static'),
        Path('static'),
        Path(os.getcwd()) / 'static',
        Path('/var/task/static'),
        Path('/vercel/path0/static'),
    ]
    
    file_path = None
    for static_dir in possible_dirs:
        if not static_dir.exists():
            continue
            
        try:
            # 尝试解码后的路径
            file_path = static_dir / decoded_path
            if file_path.exists() and file_path.is_file():
                file_path = file_path.resolve()
                static_dir_resolved = static_dir.resolve()
                # 安全检查
                if str(file_path).startswith(str(static_dir_resolved)):
                    break
            
            # 尝试原始路径（未解码）
            file_path = static_dir / path
            if file_path.exists() and file_path.is_file():
                file_path = file_path.resolve()
                static_dir_resolved = static_dir.resolve()
                # 安全检查
                if str(file_path).startswith(str(static_dir_resolved)):
                    break
            
            file_path = None
        except Exception as e:
            continue
    
    if file_path and file_path.exists() and file_path.is_file():
        # 设置正确的Content-Type
        mimetype = None
        if file_path.suffix.lower() in ['.jpg', '.jpeg']:
            mimetype = 'image/jpeg'
        elif file_path.suffix.lower() == '.png':
            mimetype = 'image/png'
        
        # 添加缓存头，优化加载速度
        response = send_file(file_path, mimetype=mimetype)
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        return response
    else:
        # 如果所有路径都失败，返回404
        abort(404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print('=' * 60)
    print('🚇 Metro Trade - Trueque en el Metro')
    print('=' * 60)
    print(f'✅ 服务启动成功')
    print(f'📱 访问地址: http://localhost:{port}')
    print(f'📦 地铁交易: http://localhost:{port}/')
    print('=' * 60)
    print('🛑 按 Ctrl+C 停止服务')
    print('=' * 60)
    print('')
    app.run(host='0.0.0.0', port=port, debug=True)

