#!/usr/bin/env python3
"""
将书籍的"我的阅读故事"从中文翻译为西班牙语
"""

# 翻译映射（中文 -> 西班牙语）
TRANSLATIONS = {
    # 1. Pedro Páramo
    '这本书不是用眼睛读的，是用耳朵听的。寂静的科马拉村里，每一个石阶、每一阵风都在转述亡灵的对话。我迷失在时间的碎片里，分不清叙述者是活人还是鬼魂。读完合上书，仿佛自己也成了那个村庄的一部分——那个被罪孽与记忆永恒困住的地方。': 
    'Este libro no se lee con los ojos, se escucha con los oídos. En el silencioso pueblo de Comala, cada escalón de piedra, cada ráfaga de viento transmite las conversaciones de las almas. Me perdí en los fragmentos del tiempo, sin poder distinguir si el narrador era un vivo o un fantasma. Al cerrar el libro, sentí que también me había convertido en parte de ese pueblo—ese lugar eternamente atrapado por el pecado y la memoria.',
    
    # 2. Obra completa de Juan Rulfo
    '如果说《佩德罗·帕拉莫》是一座迷宫，那这部全集就是整个鲁尔福的宇宙。那些短篇像一把把锋利又沉默的刀，精准地剖开墨西哥大地的孤独与坚韧。读完后，那片干旱、暴烈又充满神性的土地，永远地印在了我心里。':
    'Si "Pedro Páramo" es un laberinto, esta obra completa es todo el universo de Rulfo. Esos cuentos son como cuchillos afilados y silenciosos que diseccionan con precisión la soledad y la resistencia de la tierra mexicana. Después de leerlos, esa tierra árida, violenta y llena de divinidad quedó grabada para siempre en mi corazón.',
    
    # 3. La muerte de Artemio Cruz
    '跟随一个垂死革命者的意识，我经历了墨西哥二十世纪的波澜壮阔与道德崩解。富恩特斯用"你"、"我"、"他"三种人称，让我同时成为叙述者、审判者和旁观者。这不仅仅是一个人的死亡，更是一个理想如何被权力与时间腐蚀的全过程。':
    'Siguiendo la conciencia de un revolucionario moribundo, experimenté la grandeza y la desintegración moral del México del siglo XX. Fuentes usa los pronombres "tú", "yo" y "él" para hacerme simultáneamente narrador, juez y espectador. Esto no es solo la muerte de una persona, sino todo el proceso de cómo un ideal es corrompido por el poder y el tiempo.',
    
    # 4. Del amor y otros demonios
    '马尔克斯收起了宏大的"百年"叙事，转而讲述一个关于偏执与纯真的悲剧。少女被爱情和迷信共同囚禁，那长达22米的头发是生命力的象征，也是无形的枷锁。这个故事像一首忧伤的挽歌，讲述着以爱为名的伤害。':
    'Márquez deja de lado la gran narrativa de "Cien años" y cuenta una tragedia sobre la paranoia y la inocencia. La joven está prisionera tanto del amor como de la superstición, y sus 22 metros de cabello son símbolo de vitalidad pero también una cadena invisible. Esta historia es como una elegía triste que habla del daño hecho en nombre del amor.',
    
    # 5. Cien años de soledad
    '第一次读时，我被那些重名的人绕得晕头转向；第二次读，我看到了一个家族的命运如何像DNA一样螺旋循环；第三次读，我忽然明白，"孤独"不是一个人的状态，而是一个文明在狂欢与遗忘中不断重复的宿命。':
    'La primera vez que lo leí, me confundí con todos esos nombres repetidos; la segunda vez, vi cómo el destino de una familia gira en espiral como el ADN; la tercera vez, de repente entendí que la "soledad" no es el estado de una persona, sino el destino de una civilización que se repite constantemente entre el júbilo y el olvido.',
    
    # 6. Los detectives salvajes
    '这本书是献给所有文学青年的情书与挽歌。我跟着两个"本能现实主义诗人"横跨大洲，寻找一个失踪的作家。前半部分是青春的火焰，后半部分是灰烬的余温。它让我明白，追寻文学本身，就是一场盛大而悲壮的流浪。':
    'Este libro es una carta de amor y una elegía para todos los jóvenes literarios. Seguí a dos "poetas realistas instintivos" a través de continentes, buscando a un escritor desaparecido. La primera parte es la llama de la juventud, la segunda es el calor residual de las cenizas. Me hizo entender que buscar la literatura en sí misma es un vagabundeo grandioso y trágico.',
    
    # 7. Papeles falsos
    '这不是传统的小说，而是一场关于阅读与身份的优雅漫游。作者在纽约的街道和图书馆里，追踪一位几乎被遗忘的诗人。我感受到一种奇妙的共鸣：在一个不属于自己的城市里，用文字构建栖身之所，我们每个人不都在使用着某种"假证件"吗？':
    'No es una novela tradicional, sino una elegante deriva sobre la lectura y la identidad. La autora rastrea a un poeta casi olvidado por las calles y bibliotecas de Nueva York. Sentí una extraña resonancia: en una ciudad que no nos pertenece, construyendo un refugio con palabras, ¿no estamos todos usando algún tipo de "documento falso"?',
    
    # 8. Los rituales del caos
    '蒙西瓦伊斯是墨西哥社会最敏锐的"文化诊断师"。读他的杂文，就像在看一部快节奏的蒙太奇电影：亡灵节、革命壁画、电视肥皂剧、政治丑闻……他让我发现，理解一个民族，不仅要看它的史诗，更要看它的八卦、笑话和流行文化。':
    'Monsiváis es el "diagnosticador cultural" más agudo de la sociedad mexicana. Leer sus ensayos es como ver una película de montaje rápido: Día de Muertos, murales revolucionarios, telenovelas, escándalos políticos... Me hizo descubrir que para entender una nación, no solo hay que ver su épica, sino también sus chismes, chistes y cultura popular.',
    
    # 9. La reina del sur
    '虽然作者是西班牙人，但他刻画了一个令人难忘的墨西哥女性毒枭形象。我震惊于故事的现实感，它没有简单的黑白对立，而是展示了在暴力与利益的灰色地带，一个人如何从受害者变为掌控者。这是一部关于生存与权力的冷酷史诗。':
    'Aunque el autor es español, creó una imagen inolvidable de una narcotraficante mexicana. Me impactó el realismo de la historia: no hay una simple oposición entre el bien y el mal, sino que muestra cómo en la zona gris entre la violencia y el interés, una persona pasa de víctima a controladora. Es una épica fría sobre la supervivencia y el poder.',
    
    # 10. La noche de Tlatelolco
    '波尼亚托夫斯卡将话筒递给了墨西哥城最边缘的青少年帮派成员。他们的语言粗糙、暴力，却又充满令人心碎的脆弱。读完我才明白，"破角"不仅指他们，也指这个让他们绝望的社会。这是一本需要勇气去面对的书。':
    'Poniatowska le pasó el micrófono a los miembros de pandillas juveniles más marginados de la Ciudad de México. Su lenguaje es áspero, violento, pero también lleno de una vulnerabilidad desgarradora. Después de leerlo, entendí que "los rotos" no solo se refiere a ellos, sino también a la sociedad que los desespera. Este es un libro que requiere coraje para enfrentarlo.',
    
    # 11. El libro de arena
    '博尔赫斯用最简短的故事，构建了最令人恐惧的哲学迷宫。那本无始无终的"沙之书"，最终因它的无限而被主人抛弃。这像极了我们对知识、对宇宙的渴望与恐惧——我们真正害怕的，也许是那个没有边界、无法掌握的真相。':
    'Borges construye el laberinto filosófico más aterrador con las historias más breves. Ese "libro de arena" sin principio ni fin finalmente es abandonado por su dueño debido a su infinitud. Es muy parecido a nuestro anhelo y miedo hacia el conocimiento y el universo—lo que realmente tememos tal vez sea esa verdad sin límites e incomprensible.',
    
    # 12. Piedra de sol
    '我试着朗读，让西班牙语的音节在唇齿间滚动。帕斯的诗句像一条意识流的长河，将阿兹特克神话、现代爱情、历史记忆全部溶解其中。584行，首尾相连，形成时间的完美循环。那一刻，我感受到诗歌不是装饰，而是一种感知世界的古老而精密的方式。':
    'Intenté leerlo en voz alta, dejando que las sílabas del español rodaran entre mis labios. Los versos de Paz son como un largo río de conciencia que disuelve mitos aztecas, amor moderno y memoria histórica. 584 líneas, conectadas de principio a fin, forman un círculo perfecto del tiempo. En ese momento, sentí que la poesía no es decoración, sino una forma antigua y precisa de percibir el mundo.',
    
    # 13. La historia de mis dientes
    '一位拍卖师为名人牙齿编造荒诞又富有哲思的故事。路易塞利以一种轻盈的幽默，探讨了叙事的力量——我们如何通过故事赋予物品（乃至人生）价值。这本书让我笑出声，也让我思考：我们每个人，不都在讲述着自己版本的"牙齿故事"吗？':
    'Un subastador inventa historias absurdas y filosóficas sobre los dientes de celebridades. Luiselli explora con un humor ligero el poder de la narrativa—cómo damos valor a los objetos (e incluso a la vida) a través de historias. Este libro me hizo reír y también pensar: ¿no estamos todos contando nuestra propia versión de "historias de dientes"?',
    
    # 14. Como agua para chocolate
    '这是一本会"调味"的书！每个章节前的食谱，随着女主角蒂塔的情绪，让食物成为情感的魔法。当她悲伤时，客人吃了她的蛋糕会痛哭流涕。我读着读着，仿佛也尝到了爱情的炽热、禁锢的苦涩和自由的甘甜。这是一场感官与心灵的盛宴。':
    '¡Este es un libro que "sazona"! Las recetas antes de cada capítulo, siguiendo las emociones de la protagonista Tita, convierten la comida en magia emocional. Cuando está triste, los invitados que comen su pastel lloran a lágrimas. Mientras leía, sentí que también probaba el ardor del amor, la amargura del encierro y la dulzura de la libertad. Es un banquete para los sentidos y el alma.',
    
    # 15. El principito
    '小时候读，这是一个关于玫瑰和狐狸的童话；成年后读，这是一面照见自己如何变成"大人"的镜子。"真正重要的东西，用眼睛是看不见的。" 这句话在不同的年龄，有不同的重量。它提醒我，不要忘记自己也曾是B612星球上的那个孩子。':
    'De niño, lo leí como un cuento sobre una rosa y un zorro; de adulto, es un espejo que refleja cómo me convertí en "adulto". "Lo esencial es invisible a los ojos." Esta frase tiene diferente peso a diferentes edades. Me recuerda que no debo olvidar que también fui ese niño del planeta B612.',
    
    # 16. Hábitos atómicos
    '在读完那么多关于命运与孤独的宏大叙事后，这本书像一份实用的生活工具书。它告诉我，宏大的改变始于微小的、1%的日常积累。它让我从文学的天空落回现实的地面，开始耐心地、系统地建造自己想要的生活。':
    'Después de leer tantas grandes narrativas sobre el destino y la soledad, este libro es como una herramienta práctica para la vida. Me dice que los grandes cambios comienzan con pequeñas acumulaciones diarias del 1%. Me hizo bajar del cielo literario a la tierra de la realidad, comenzando a construir pacientemente y sistemáticamente la vida que quiero.',
    
    # 17. La región más transparente
    '这是富恩特斯为墨西哥城写下的"肖像小说"。我仿佛漫步在改革大道上，与形形色色的角色擦肩而过：革命新贵、没落贵族、艺术家、骗子……他们共同构成了这座城市的喧嚣与虚无。"最明净的地区"这个充满讽刺的标题，道尽了现代化光环下的混乱与矛盾。':
    'Esta es la "novela retrato" que Fuentes escribió para la Ciudad de México. Caminé por el Paseo de la Reforma, rozándome con diversos personajes: nuevos ricos de la revolución, nobles decadentes, artistas, estafadores... Juntos forman el bullicio y la vacuidad de esta ciudad. El título irónico "La región más transparente" expresa perfectamente el caos y la contradicción bajo el halo de la modernización.'
}

def translate_stories():
    """翻译HTML中的故事"""
    from pathlib import Path
    
    html_file = Path(__file__).parent / 'templates' / 'index.html'
    
    print("=" * 60)
    print("🌐 翻译阅读故事为西班牙语")
    print("=" * 60)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    translated_count = 0
    for chinese, spanish in TRANSLATIONS.items():
        if chinese in content:
            content = content.replace(chinese, spanish)
            translated_count += 1
            print(f"✅ 已翻译: {chinese[:30]}...")
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 共翻译 {translated_count} 个故事")
    return translated_count

if __name__ == "__main__":
    translate_stories()

