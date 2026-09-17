# -*- coding: utf-8 -*-
"""场景脚本数据：P0~P10 全部剧情节点，正典台词与旁白整理自《素材文本/原文剧本.txt》。

Beat 类型：
  narration  旁白（修二第一人称，文学化）
  line       角色台词（who/say/expr/action）
  me         玩家（修二）台词（推进用，展示后继续）
  choice     选项（正典选项 + 允许自由输入，由规则引擎应答后继续）
  effect     世界效果（flags/affection/advance/location/time）
  free       自由输入点（无正典选项，纯开放）
"""

SCENES = {}

# ================================================================ P1 初遇
SCENES['P1'] = {
    'title': 'P1 · 初遇',
    'location': 'oldhouse_in',
    'time': 'day',
    'bg': 'bg_oldhouse_corridor.png',
    'beats': [
        {'type': 'narration', 'text': '悲伤，犹如穿过蒙着水汽的窗玻璃照射进来的阳光，模糊而若有若无。父亲和母亲去世了——对我来说，这无比悲戚而沉重的现实，却是那么的平淡无奇。'},
        {'type': 'narration', 'text': '亲戚们总是将简单的道理，说得很拐弯抹角。他们围绕着同一个话题，商议了好几个小时——在亲戚中，到底由谁来收养我。必须有人来抽到这个下下签。'},
        {'type': 'line', 'who': 'relative_man', 'say': '麻烦呐――', 'expr': 'normal', 'action': '（他推了推眼镜，视线游移开）'},
        {'type': 'line', 'who': 'relative_woman', 'say': '虽然我不想直说――', 'expr': 'normal', 'action': '（她用手掩着嘴）'},
        {'type': 'line', 'who': 'relative_man', 'say': '所以谁来――', 'expr': 'normal', 'action': '（长辈们的争论声越来越大）'},
        {'type': 'narration', 'text': '我一个人躲在房间的角落，不去听他们高声争论的内容，一直眺望着檐廊外的风景。白雪在冰冷的天空中，寂静地飞舞着。'},
        {'type': 'narration', 'text': '这时，我感觉有人靠近了这边。'},
        {'type': 'line', 'who': 'miyuki', 'say': '呐', 'expr': 'normal', 'action': '（不知何时，一个女孩子伫立在离我稍远些的地方。她远离长辈们，在一旁凝视着我。仿佛像已这样守望了我许多年）'},
        {'type': 'narration', 'text': '她没有开口说话，只是默默无言地凝视着我。我感觉只有她身周的氛围有些不同——清澈透明，让人感到安心。'},
        {'type': 'line', 'who': 'miyuki', 'say': '我们去外面玩吧', 'expr': 'smile', 'action': ''},
        {'type': 'line', 'who': 'miyuki', 'say': '因为你，看起来有点无聊哦', 'expr': 'smile', 'action': '（像是看透了我的心思一样）'},
        {'type': 'narration', 'text': '她忽然握住了我的手。乌黑的长发随着她的脚步走动，轻轻地沙沙作响。她牵着我的手，穿过如同深海一般深邃的走廊。'},
        {'type': 'free', 'prompt': '被陌生的女孩子牵手，你想说什么？', 'chips': ['……你是谁呀？', '放开我啦！', '……']},
        {'type': 'line', 'who': 'miyuki', 'say': '我们走吧', 'expr': 'smile', 'action': '（她有点用力地拽着我的胳膊）'},
        {'type': 'effect', 'location': 'courtyard', 'bg': 'bg_courtyard.png'},
        {'type': 'narration', 'text': '好耀眼——纯白的色彩尽染了整个世界。可以说是一片白暗。冬天的阳光是那么微弱无力，太阳在厚重乌云的另一边微微晃动着。'},
        {'type': 'line', 'who': 'miyuki', 'say': '呼，好冷啊', 'expr': 'smile', 'action': '（她有些开心地耸了耸肩膀，白色的呼气如同热浪一样，溶化在空气中）'},
        {'type': 'line', 'who': 'miyuki', 'say': '呐，你喜欢雪吗？', 'expr': 'normal', 'action': '（得到解放的她像肋下生出了双翅，在这片凄清冷寂的天地中欢快地奔走）'},
        {'type': 'narration', 'text': '到底喜欢雪还是不喜欢，我并没有认真地考虑过。我想，我是憎恶着雪的吧。这雪吞没了我的父亲和母亲……明明是如此，但我却怎么都对它恨不起来。'},
        {'type': 'choice', 'options': [
            {'label': '……我喜欢这雪', 'intents': ['like_snow'], 'affection': 3, 'flag': 'likes_snow', 'axis': {'bond': 2}},
            {'label': '我…不了解…', 'intents': ['smalltalk'], 'affection': 0},
            {'label': '（长久地沉默）', 'intents': ['smalltalk'], 'affection': 1},
        ]},
        {'type': 'narration', 'text': '听到我的回答，女孩子脸上绽开了微笑。在这冰天雪地之中，只有她露出了饱含温暖的微笑。她张开双臂，手舞足蹈地转了一圈。'},
        {'type': 'cg', 'img': 'cg01.png', 'caption': '雪之妖精'},
        {'type': 'narration', 'text': '雪一直静静地下着。雪之妖精——如果雪之妖精真的存在，那她的容貌一定与我眼前的这个女孩别无二致。'},
        {'type': 'effect', 'flags': {'met_miyuki': True}, 'affection': 2, 'cast_remove': ['relative_man', 'relative_woman']},
    ],
}

# ================================================================ P2 清雪
SCENES['P2'] = {
    'title': 'P2 · 清雪',
    'location': 'courtyard',
    'time': 'day',
    'bg': 'bg_courtyard.png',
    'beats': [
        {'type': 'narration', 'text': '老屋的周围，积了很深的雪。庭院中的树木，都化上了一层银白的妆。橡胶长靴深深地陷入像纯棉一样松软的积雪中。'},
        {'type': 'line', 'who': 'miyuki', 'say': '给，这是你的', 'expr': 'smile', 'action': '（她两手各拿着一把铲子，得意地把左手的铲子递给了我）'},
        {'type': 'choice', 'options': [
            {'label': '哎……我的？', 'intents': ['smalltalk'], 'affection': 0},
            {'label': '我知道啊！', 'intents': ['accept'], 'affection': 2},
        ]},
        {'type': 'line', 'who': 'miyuki', 'say': '用这个清雪', 'expr': 'normal', 'action': ''},
        {'type': 'line', 'who': 'miyuki', 'say': '清雪……你不知道吗？', 'expr': 'normal', 'action': ''},
        {'type': 'narration', 'text': '为什么要我清扫这些雪啊。内心渐渐产生了委屈的情绪。但女孩子并没有因我的不满而慌张。她率先挥起铲子，麻利地开始清扫地上的雪。'},
        {'type': 'line', 'who': 'miyuki', 'say': '到了明天早晨，这里就结冰了。所以，今天好歹要把积雪清扫一下', 'expr': 'normal', 'action': ''},
        {'type': 'line', 'who': 'miyuki', 'say': '而且，锻炼一下身体很不错哦。心情也变得爽朗起来，不会再烦躁了', 'expr': 'smile', 'action': ''},
        {'type': 'narration', 'text': '我没办法，只好开始陪她清雪。铲子的前端斜刺入了刚刚积落的新雪中。虽然这样的劳动很单调，但专心地去做，身体也渐渐暖和起来。'},
        {'type': 'line', 'who': 'miyuki', 'say': '很好……你做得很不错嘛', 'expr': 'smile', 'action': '（她在一旁对我露出了微笑）'},
        {'type': 'narration', 'text': '在活动身体的过程中，脑海中泛起了许多有关过去的回忆。过去，像这样在庭院中清雪的，总是我的父亲。而幼年的我，就在檐廊下静静地看着他。晚餐的香气从厨房飘来。是母亲准备好了一家人吃的饭。'},
        {'type': 'narration', 'text': '家人——不意间，一阵空茫的风吹拂过我的心。我的心中像是开了一个空洞，只听得到干燥的风声从中穿过，猎猎作响。'},
        {'type': 'me', 'say': '呜……'},
        {'type': 'narration', 'text': '忽然，我不禁发出一阵呜咽。脸上就像打开了水龙头似的，涕泗横流。滚烫而酸楚的泪水，流进了口中，落到雪地上，留下了星星点点的痕迹。'},
        {'type': 'narration', 'text': '这时，我终于感到痛彻心扉，流下了真正属于悲伤的泪水。温柔地守护着我，呼唤着我的名字的父亲与母亲，再也不会回到我的身边了。'},
        {'type': 'line', 'who': 'miyuki', 'say': '不要哭了……男孩子可是不能哭的哦', 'expr': 'normal', 'action': '（她安慰着我说道。比刚刚要温柔，离我的距离也比刚刚更近。她张开臂膀，环抱住了我的头）'},
        {'type': 'cg', 'img': 'cg02.png', 'caption': '想哭就哭出来吧'},
        {'type': 'narration', 'text': '温暖令人感怀的气息，仿佛阳光下晒过的被子那样的味道，扑鼻而来。我留恋着她的气味，不想离开，就这样一直哭泣着。'},
        {'type': 'choice', 'options': [
            {'label': '（任由她抱着，继续哭）', 'intents': ['cry'], 'affection': 3, 'flag': 'comforted', 'axis': {'bond': 3}},
            {'label': '（想从她怀里挣脱）', 'intents': ['refuse'], 'affection': 1, 'flag': 'comforted', 'axis': {'bond': 1}},
        ]},
        {'type': 'line', 'who': 'miyuki', 'say': '可是……事到如今，想哭就哭出来吧。我会把脸挡住的……', 'expr': 'sad', 'action': '（她轻抚着我的背。手抚过的地方是无尽的温柔）'},
        {'type': 'narration', 'text': '我哭得累了，之后便回到自己的房间，沉入了梦乡。醒来的时候，发现那个女孩子已经不见了。'},
        {'type': 'narration', 'text': '我在鸟羽老人家度过了一晚。到了第二天，便漫无目的地到街上游荡。随心所欲地晃来晃去，最后还是回到了那间老屋前。'},
        {'type': 'effect', 'flags': {'snow_cleared': True, 'comforted': True}, 'location': 'toba_home', 'bg': 'bg_toba_home.png', 'time': 'night', 'cast_remove': ['miyuki']},
    ],
}

# ================================================================ P3 空屋与雪仗
SCENES['P3'] = {
    'title': 'P3 · 你的姐姐啊',
    'location': 'oldhouse_in',
    'time': 'evening',
    'bg': 'bg_oldhouse_room.png',
    'beats': [
        {'type': 'narration', 'text': '这里已经没有住户了，家中也褪去了往日的色彩，显得冷冷清清。这栋房子，也和它的所有者一起死去了吗。'},
        {'type': 'narration', 'text': '我打开旧柜子的抽屉，盯着挂在镜框里的奖状上那我不会读的汉字。取出父亲用过的、沾满烟草味道的被子，趴在上面滚来滚去。结了冰的记忆，慢慢地得到解冻。'},
        {'type': 'narration', 'text': '视线无意地彷徨着，看到了挂在墙上的时钟。那是在多年前就已不再走动的时钟。我踩在小饭桌上把它取了下来——时针和分针，停留在４时４９分这个没有着落的数字上。'},
        {'type': 'me', 'say': '动不了吗……？'},
        {'type': 'narration', 'text': '坏掉的时钟，说到底都不会再转动了。虽然我感到有些悲伤，但却不会哭泣。只是心中浮现出了些淡然而微茫的情绪，有些冰冷。'},
        {'type': 'narration', 'text': '……哎？好像有人从楼梯上走下来了。亲戚们——已然全都回去了。说是小偷——这家中也没什么值钱的东西。脚步声离我越来越近。走廊上发出了吱呀的声响。'},
        {'type': 'narration', 'text': '夕阳光从檐廊照射了进来。那个人的身影，落在了夕阳光照射着的走廊上。'},
        {'type': 'me', 'say': '哈啊……？'},
        {'type': 'line', 'who': 'miyuki', 'say': '欢迎回来哦', 'expr': 'smile', 'action': '（她的态度很自然，仿佛这里是她的家一般。自然到了让我目瞪口呆的地步）'},
        {'type': 'narration', 'text': '露出脸的，是那个女孩子。是从清雪那天以来，便消失不见了的、那个比我稍稍年长的女孩子。'},
        {'type': 'choice', 'options': [
            {'label': '你，是谁啊？', 'intents': ['ask_identity'], 'affection': 0},
            {'label': '（吓得说不出话）', 'intents': ['smalltalk'], 'affection': 1, 'axis': {'bond': 1}},
        ]},
        {'type': 'line', 'who': 'miyuki', 'say': '我？我是――', 'expr': 'normal', 'action': ''},
        {'type': 'line', 'who': 'miyuki', 'say': '你的姐姐啊', 'expr': 'smile', 'action': ''},
        {'type': 'narration', 'text': '我不懂她在说什么。姐姐……我从没听说过，自己还有一个姐姐。这简直是天方夜谭。'},
        {'type': 'choice', 'options': [
            {'label': '我根本没有什么姐姐，你这个骗子！', 'intents': ['call_liar'], 'affection': 0, 'flag': 'called_liar'},
            {'label': '（愣在原地）', 'intents': ['smalltalk'], 'affection': 1, 'flag': 'called_liar', 'axis': {'bond': 1}},
        ]},
        {'type': 'line', 'who': 'miyuki', 'say': '我没有骗你', 'expr': 'normal', 'action': '（即便如此，她的表现依然很平静）'},
        {'type': 'line', 'who': 'miyuki', 'say': '我都说了这不是骗你', 'expr': 'normal', 'action': '（我被她那气定神闲的自信感所镇住了。反过来，反抗心也愈加强烈）'},
        {'type': 'narration', 'text': '我对她丢下抗议的话，从檐廊下飞奔到了庭院中。她好像从背后追上来了。真是让我不快。所以，我假装滑倒的样子，完美地摔在了雪地上。'},
        {'type': 'line', 'who': 'miyuki', 'say': '……没事吧？', 'expr': 'surprise', 'action': '（听她的声音，似乎很担心。一切都在我的计划之中）'},
        {'type': 'narration', 'text': '我一跃而起，将雪球朝她扔去。白色的雪块打在了女孩子的脸上——这下她的头发、鼻子和嘴角，都沾上了雪。'},
        {'type': 'me', 'say': '嘿嘿，丑八怪'},
        {'type': 'line', 'who': 'miyuki', 'say': '呀啊！？', 'expr': 'surprise', 'action': ''},
        {'type': 'narration', 'text': '我挺胸抬头，宣示胜利。她想哭就哭出来吧。我如此想着——忽然，我被雪球打中了。'},
        {'type': 'me', 'say': '呜哇啊！？'},
        {'type': 'line', 'who': 'miyuki', 'say': '以牙还牙！', 'expr': 'smile', 'action': '（雪球接二连三向我袭来，速度飞快）'},
        {'type': 'narration', 'text': '局面演变成混战。我反击了两次，却被她打中了四次。我重重地摔倒在地上——这简直是单方面的虐杀。被欺负得都要哭了。'},
        {'type': 'me', 'say': '呜……呜呜……嗯，呜…呜呜……'},
        {'type': 'line', 'who': 'miyuki', 'say': '……抱歉哦？你很痛吗……？', 'expr': 'surprise', 'action': '（她一脸担心地向我跑了过来。然而我甩开她的手，一跃而起）'},
        {'type': 'me', 'say': '傻ー瓜！丑八ー怪！'},
        {'type': 'narration', 'text': '我运用着所掌握不多的词汇量，说出了绞尽脑汁才想出的台词。然后便逃了出去。'},
        {'type': 'effect', 'flags': {'snowball_fight': True, 'accepted_sister': False}, 'affection': 3},
    ],
}

# ================================================================ P4 冬祭之夜
SCENES['P4'] = {
    'title': 'P4 · 冬祭之夜',
    'location': 'shrine_road',
    'time': 'night',
    'bg': 'bg_town_night_festival.png',
    'beats': [
        {'type': 'narration', 'text': '祭典之夜降临了。冬天的小镇，仿佛回到春天了似的十分热闹。太阳消失在了山脊的另一边，地上燃起了熊熊的篝火。赤色的光，星星点点地渐次浮现，照亮了通往神社的山路。'},
        {'type': 'narration', 'text': '太鼓的乐声接连不断传来。夜幕降临，镇上的老少男女，便一齐向山上进发。我们随波逐流，跟着人群向前进发。她用白皙而纤细的手牵着我。'},
        {'type': 'choice', 'options': [
            {'label': '好啦，你放开我吧', 'intents': ['refuse'], 'affection': 0, 'axis': {'worldly': 1}},
            {'label': '（默默让她牵着）', 'intents': ['accept'], 'affection': 2, 'axis': {'bond': 2}},
        ]},
        {'type': 'line', 'who': 'miyuki', 'say': '不行。我们要是走散就坏了', 'expr': 'normal', 'action': '（女孩子紧紧抓着我的手不放，反而越来越用力）'},
        {'type': 'narration', 'text': '漫长的参道两旁，夜市的摊子一个挨着一个。电灯泡发出的光芒炫目至极。明明是深冬季节，这里却热得人大汗淋漓。即便如此，群山的夜依旧深沉。'},
        {'type': 'narration', 'text': '靠近神社，黑暗又浓了一分。光亮无法抵达的地方，黑暗也显得更加深重。有种被潜藏在漆黑空间另一边的可怕东西凝视着的感觉。不知不觉中，我感觉自己的手被握得更紧。'},
        {'type': 'line', 'who': 'miyuki', 'say': '不要紧――', 'expr': 'normal', 'action': '（她仿佛察觉了我的不安一般，在我的耳边低语）'},
        {'type': 'effect', 'location': 'shrine', 'bg': 'bg_shrine_night.png'},
        {'type': 'narration', 'text': '神社里面已经挤满了熙熙攘攘的人群。太鼓声与笛声和人声交混在一起。篝火通明，大锅中冒着腾腾的白气。燃起的火花将黑暗的夜空映得一片通红。'},
        {'type': 'narration', 'text': '在红与黑之间浮现的这副光景，如同幻境一般，让人觉得这里不属于人世。'},
        {'type': 'narration', 'text': '——归途。夜风渐冷，我的脚在人群里受了伤，每走一步都隐隐作痛。她注意到了我的异样，在我面前蹲下了身子。'},
        {'type': 'line', 'who': 'miyuki', 'say': '嗯，我知道啦。快点吧', 'expr': 'smile', 'action': '（她朝我笑了笑，示意我趴上去）'},
        {'type': 'narration', 'text': '我屈服在了女孩子纯真的笑容之下，小心翼翼地攀上了她的背。这个女孩子的身体明明看起来很纤弱，但却十分有力。'},
        {'type': 'line', 'who': 'miyuki', 'say': '好了吗？那我们出发吧――', 'expr': 'smile', 'action': ''},
        {'type': 'line', 'who': 'miyuki', 'say': '小修要抓紧我一点啊。姐姐也要靠着小修，暖和一下', 'expr': 'smile', 'action': ''},
        {'type': 'cg', 'img': 'cg03.png', 'caption': '下山的背'},
        {'type': 'narration', 'text': '悠悠地，悠悠地——仿佛在月夜之海中轻摇，世界缓缓地向一边倾斜，而后又变得平稳。我是一叶小舟，而她便是那清波。'},
        {'type': 'narration', 'text': '――摇啊摇，摇啊摇，山里的小狐狸也不吵。摇啊摇，摇啊摇，山里的小斑鸠也不闹――她唱起了歌谣。那是一首古老的、我未曾听过的歌谣。'},
        {'type': 'me', 'say': '好冷……'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修……睡着了吗？', 'expr': 'normal', 'action': '（歌声与夜风融为一体，传入半睡半醒的我耳畔）'},
        {'type': 'narration', 'text': '我的不安消失了。如今，只想被身上的温暖与香味所围绕。明天，若是我的脚好了……她若是与往常一般，等我来那老屋……若是如此……那陪她多玩上一会也无妨。'},
        {'type': 'effect', 'flags': {'festival_done': True, 'foot_hurt': True}, 'affection': 5, 'location': 'oldhouse_front', 'bg': 'bg_courtyard.png'},
    ],
}

# ================================================================ P5 刻身高
SCENES['P5'] = {
    'title': 'P5 · 刻身高',
    'location': 'oldhouse_in',
    'time': 'night',
    'bg': 'bg_oldhouse_room_night.png',
    'beats': [
        {'type': 'line', 'who': 'miyuki', 'say': '今年也快到头了', 'expr': 'normal', 'action': '（炉边。我心不在焉地抬起头，望向窗外的寒冷天空）'},
        {'type': 'line', 'who': 'miyuki', 'say': '外面――下雪了吗', 'expr': 'normal', 'action': ''},
        {'type': 'narration', 'text': '雪。我和她相遇的那一天，那雪也像今天这样，一直在无声无息地下。从那以后。'},
        {'type': 'me', 'say': '……那一天也下了雪'},
        {'type': 'line', 'who': 'miyuki', 'say': '那一天？', 'expr': 'normal', 'action': ''},
        {'type': 'choice', 'options': [
            {'label': '……父亲和母亲…没有回来的那一天……', 'intents': ['ask_parents'], 'affection': 2, 'flag': 'parents_belief', 'axis': {'obsession': 4}},
            {'label': '（摇头，岔开话题）', 'intents': ['smalltalk'], 'affection': 0, 'axis': {'worldly': 2}},
        ]},
        {'type': 'narration', 'text': '压抑的沉默，横亘在我们中间。我本来没想提及父母的事，然而一旦开了口，便再难以停下。'},
        {'type': 'me', 'say': '他们都说，父亲和母亲已经去世了……但我还是相信，他们还在那座深山里面'},
        {'type': 'me', 'say': '在那里呼唤着我。我一看到这白雪，心里就不由得那么想……'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修……', 'expr': 'sad', 'action': '（她脸上的笑容不见了。而后目光有些难过地低垂了下去。我像是做了很过分的事一样，感到坐立不安起来）'},
        {'type': 'narration', 'text': '沉默。而后——'},
        {'type': 'line', 'who': 'miyuki', 'say': '呐――', 'expr': 'smile', 'action': '（她露出了一如往常的笑容。悲伤在转瞬之间，已然消失得无影无踪）'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修，我帮你量量身高吧', 'expr': 'smile', 'action': ''},
        {'type': 'me', 'say': '身高？'},
        {'type': 'line', 'who': 'miyuki', 'say': '嗯。从今以后，姐姐每年都会为你量身高', 'expr': 'smile', 'action': ''},
        {'type': 'narration', 'text': '难以达成的约定。如泡沫般脆弱的关系。如同漂流瓶中的信，漂洋过海，不知道最终会搁浅在哪一片海滩。一切都模糊而飘忽不定——但它却十分美好，让我愿意去相信它。'},
        {'type': 'line', 'who': 'miyuki', 'say': '就刻在那边的柱子上好了', 'expr': 'normal', 'action': '（她把我带到了壁龛那厚实的柱子前）'},
        {'type': 'narration', 'text': '衣柜上放着父亲的一把裁纸刀。姐姐用它，在年久泛黄的柱上，刻下了一道痕。我帮她完成了这个幼稚可笑的仪式，感到很是难为情。'},
        {'type': 'cg', 'img': 'cg04.png'},
        {'type': 'line', 'who': 'miyuki', 'say': '今年到这里……吧', 'expr': 'normal', 'action': '（裁纸刀在柱上划出一道浅浅的痕）'},
        {'type': 'narration', 'text': '回过神的时候，夜幕早已降临。夜幕降临，我便不得不回去了。离开这个时光在此停滞、让我得以短暂停留于此的老屋。'},
        {'type': 'me', 'say': '……我走了'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修，说好了哦。明年也要――', 'expr': 'smile', 'action': ''},
        {'type': 'line', 'who': 'miyuki', 'say': '……呐？', 'expr': 'smile', 'action': '（她向我伸出了白皙的小拇指。目光凝视着我。约定。明年。柱上的痕。一切一切，都不像发生在真实的世界中）'},
        {'type': 'me', 'say': '……我回去了'},
        {'type': 'narration', 'text': '小指和小指，并没能勾在一起。'},
        {'type': 'effect', 'flags': {'height_marked': True}, 'affection': 4},
    ],
}

# ================================================================ P6 送站
SCENES['P6'] = {
    'title': 'P6 · 深雪',
    'location': 'station',
    'time': 'day',
    'bg': 'bg_station_day.png',
    'beats': [
        {'type': 'narration', 'text': '我收拾了与来时相比重量丝毫未变的行李，在茫茫飞雪与独眼老人的目送中，走向车站。雪还在下。静悄悄地簌簌而落。铅灰色的云低沉而厚重。'},
        {'type': 'narration', 'text': '我不经意间抬起头——是她在那里。她的长发被一阵寒风吹起，裙裾飞扬。女孩子在风中眯缝起了眼睛，安静地对我微笑。'},
        {'type': 'line', 'who': 'miyuki', 'say': '我把你送到车站吧', 'expr': 'smile', 'action': ''},
        {'type': 'choice', 'options': [
            {'label': '不用了啊……', 'intents': ['refuse'], 'affection': 0, 'axis': {'worldly': 1}},
            {'label': '……嗯', 'intents': ['accept'], 'affection': 2, 'axis': {'bond': 2}},
        ]},
        {'type': 'narration', 'text': '她无视了我的回应，径直向前走去。我和她肩并肩一起走，才发现她的个子比我高那么多。明年今日，又会如何呢。'},
        {'type': 'me', 'say': '对了……'},
        {'type': 'line', 'who': 'miyuki', 'say': '嗯？', 'expr': 'normal', 'action': ''},
        {'type': 'choice', 'options': [
            {'label': '……你要怎么办？', 'intents': ['ask_stay'], 'affection': 2, 'axis': {'bond': 2}},
            {'label': '（沉默）', 'intents': ['smalltalk'], 'affection': 0, 'axis': {'worldly': 1}},
        ]},
        {'type': 'line', 'who': 'miyuki', 'say': '怎么――', 'expr': 'surprise', 'action': '（她仿佛听说了不可思议的事似的，睁大了眼睛）'},
        {'type': 'line', 'who': 'miyuki', 'say': '我会在那里，一直等啊。一直', 'expr': 'normal', 'action': '（她说，要等下去。等待谁。等待什么。答案对我来说，不言而喻）'},
        {'type': 'narration', 'text': '她身上的不可思议之处，真的有很多很多。然而，我却觉得这都无所谓了。倒不如说不可思议这一点，本就和这个女孩子的气质很相符。'},
        {'type': 'narration', 'text': '单线的铁轨慢慢地拐了个弯，消失在茫茫山间。这条铁轨的尽头，是东京。电车驶入了空无一人的站台。还有十分钟不到。'},
        {'type': 'line', 'who': 'miyuki', 'say': '没落下什么东西吧？', 'expr': 'normal', 'action': ''},
        {'type': 'me', 'say': '嗯'},
        {'type': 'narration', 'text': '我走进了冷冷清清、几近无人的车厢。随便挑了个窗边的位置坐下来。'},
        {'type': 'line', 'who': 'miyuki', 'say': '多多小心啊', 'expr': 'smile', 'action': ''},
        {'type': 'narration', 'text': '这对话平淡无奇。然而，一字一句，仍然清清楚楚地传入了我的耳中。'},
        {'type': 'line', 'who': 'miyuki', 'say': '那……我们拉勾', 'expr': 'smile', 'action': '（女孩子伸出了白皙的小手指）'},
        {'type': 'me', 'say': '……嗯'},
        {'type': 'narration', 'text': '我们勾起了小指。'},
        {'type': 'cg', 'img': 'cg05.png'},
        {'type': 'line', 'who': 'miyuki', 'say': '拉～勾！', 'expr': 'smile', 'action': '（我们的手指相扣，晃一晃，结下了约定）'},
        {'type': 'me', 'say': '说谎要吞千根针'},
        {'type': 'line', 'who': 'miyuki', 'say': '那就这么约定了哦', 'expr': 'smile', 'action': ''},
        {'type': 'narration', 'text': '直到这时我才想起来。我忘了一件重要的事——我还不知道她的名字。事到如今，连「告诉我你叫什么名字吧」这句话，我都难以开口。'},
        {'type': 'choice', 'options': [
            {'label': '对了……（想问名字）', 'intents': ['ask_name'], 'affection': 2, 'axis': {'bond': 2}},
            {'label': '（终究没有问出口）', 'intents': ['smalltalk'], 'affection': 0, 'axis': {'worldly': 1}},
        ]},
        {'type': 'narration', 'text': '我在一番踌躇，无数次地重复着同一个词之后——'},
        {'type': 'line', 'who': 'miyuki', 'say': 'miyuki', 'expr': 'normal', 'action': '（女孩子呢喃着，话语声在我的耳边轻轻回响）'},
        {'type': 'line', 'who': 'miyuki', 'say': '写作深和雪两个字，miyuki', 'expr': 'smile', 'action': ''},
        {'type': 'narration', 'text': '深雪。深深积落，群山的白雪。她真的是人如其名。广播响了——车门即将关闭。我听到列车广播，急忙奔上了列车，而后上气不接下气地回头，对她说道。'},
        {'type': 'me', 'say': '我，还会回来的……'},
        {'type': 'narration', 'text': '我的话说到一半，车门便关上了。在温暖的车厢中，我透过自动门的玻璃窗，看到那个女孩子——仍是露出平常的微笑，依依不舍地向我挥了挥手。'},
        {'type': 'narration', 'text': '她微微地开了口。然而声音却已听不到。「一定会」——我想，她一定是这么说的。'},
        {'type': 'narration', 'text': '列车摇摇晃晃，缓缓地开往远方。寒风吹拂着的那个身影，一直在朝我挥手。然而转瞬之间，茫茫飞雪遮蔽了我的目光。我忽然想到——这个女孩是真实存在的人吗。'},
        {'type': 'effect', 'flags': {'left_town': True, 'knows_name': True}, 'affection': 3},
    ],
}

# ================================================================ P7 重逢
SCENES['P7'] = {
    'title': 'P7 · 欢迎回家',
    'location': 'station',
    'time': 'day',
    'bg': 'bg_station_day.png',
    'beats': [
        {'type': 'narration', 'text': '【三年后】'},
        {'type': 'narration', 'text': '广播「上山站到了，上山站到了」——慢慢地，静悄悄地，列车驶入了站台。车站与三年前相仿，空无一人。我擦去车窗上的水汽，目光自然地开始搜寻某个人的身影。令人怀恋的那张面庞，理所当然地没有出现。'},
        {'type': 'me', 'say': '…没有来…吗'},
        {'type': 'narration', 'text': '与东京不同的是，这里的空气湿润而寒冷，砭人肌骨。走出车站，正是清晨时分，田间小路在眼前一望无际地展开。阴沉的天空中，粉雪簌簌飘落。'},
        {'type': 'narration', 'text': '我找到了这里唯一的公共电话，投下硬币，用冰冷的手指拨下了自家的电话号码。电话呼叫了几十次，无人接听之后，我终于无奈地放下了听筒。心里的感觉空荡荡的，仿佛开了一个大洞。'},
        {'type': 'me', 'say': '我真是傻啊……'},
        {'type': 'narration', 'text': '约定没能实现。我不只是迟了一年。第二年，我也在现实的围城中举步维艰地生存着。然而，我唯一能做到的，只是拒绝遗忘。或许，正是坚信着我们的约定，才让我熬过了寄人篱下的辛酸岁月。'},
        {'type': 'effect', 'location': 'oldhouse_in', 'bg': 'bg_oldhouse_room.png'},
        {'type': 'narration', 'text': '久未相见的我家门口，看起来仿佛比以前生了更多的锈。三年间毫无人烟的老屋，仿佛废墟一般荒凉。弥漫着寂寥而缓慢的衰亡气息。失去了主人的老屋，仿佛正渐渐地死去。'},
        {'type': 'narration', 'text': '我向房间中窥去。那里就像昏暗的洞穴一样，没有一丝一毫的生活气息。果不其然，这里空无一人。'},
        {'type': 'me', 'say': '……哈哈哈'},
        {'type': 'narration', 'text': '一个人心中珍重的回忆，却缘起于不知和哪个小孩的一时兴起。若是有什么东西在这个不见天日、人去楼空的家中一直生活到如今的话——若是那样，那个女孩子，一定不是人类吧。妖怪、鬼魂、幽灵……'},
        {'type': 'line', 'who': 'miyuki', 'say': '咦――', 'expr': 'surprise',
         'action': '（我的背后，突然传来了声音）', 'cast': ['shuuji', 'miyuki']},
        {'type': 'me', 'say': '呜……啊……啊啊……？'},
        {'type': 'narration', 'text': '我有些吃惊，上身不稳，回过头一瞧——出现在我视线中的是——'},
        {'type': 'cg', 'img': 'cg06.png'},
        {'type': 'line', 'who': 'miyuki', 'say': '欢迎回家哦，小修', 'expr': 'smile', 'action': '（是深雪在那里。带着仿佛昨日才刚刚相见过一般、一如往常波澜不惊的笑颜）'},
        {'type': 'line', 'who': 'miyuki', 'say': '你长高了好多啊。但是，还是没有姐姐高', 'expr': 'smile', 'action': ''},
        {'type': 'me', 'say': '哎……啊……为，为什……么？'},
        {'type': 'narration', 'text': '我大吃一惊之下，只勉强挤出了几个字。当人从心底感到惊诧时，是说不出话的吧。'},
        {'type': 'line', 'who': 'miyuki', 'say': '……哎？', 'expr': 'surprise', 'action': '（而深雪对我的这一反应，却感到有些不可思议）'},
        {'type': 'choice', 'options': [
            {'label': '（追问她这三年在哪里）', 'intents': ['ask_mystery'], 'affection': 0, 'axis': {'obsession': 2}},
            {'label': '（放弃追问，任由安心感包围）', 'intents': ['accept'], 'affection': 3, 'axis': {'bond': 3}},
        ]},
        {'type': 'line', 'who': 'miyuki', 'say': '姐姐不是说过了吗，会在这里等你', 'expr': 'smile', 'action': '（她的肌肤还是和从前一样白皙通透。身高也变高了，肢体散发着健美的气息）'},
        {'type': 'narration', 'text': '这时，比起不可思议的感觉，她在老屋中对我露出的微笑，更让我感到莫名的安心。我迷迷糊糊地在被炉边睡着了。'},
        {'type': 'narration', 'text': '当我醒来的时候，眼前并不是熟悉的天花板。带着潮湿而土气味道的、有些被熏黑了的古旧天花板——那是比现在还要幼小的时候，我还是个婴儿的时候，被这世界的一切所祝福的时候。'},
        {'type': 'me', 'say': '……这是，我的家啊……'},
        {'type': 'narration', 'text': '我的被子上，落下了一丝湛蓝的光。那是从窗帘的缝隙中照射进来的清晨的光。那又是谁，为我盖上了被子呢。一股甘甜的气味，挑动着我的鼻尖。'},
        {'type': 'effect', 'flags': {'reunion_done': True}, 'affection': 5, 'location': 'oldhouse_in', 'time': 'day', 'bg': 'bg_oldhouse_room.png'},
    ],
}

# ================================================================ P8 同居日常
SCENES['P8'] = {
    'title': 'P8 · 老屋的日常',
    'location': 'oldhouse_in',
    'time': 'day',
    'bg': 'bg_oldhouse_room.png',
    'beats': [
        {'type': 'narration', 'text': '光阴如梭，几天很快地便过去了。老屋的生活有着温柔的循环：清雪、泡澡、做饭、扑克、并肩而眠。'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修，过来清雪啦――', 'expr': 'smile', 'action': ''},
        {'type': 'me', 'say': '可明天还会下雪啊，姐姐――'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修？你先去泡澡吧――', 'expr': 'normal', 'action': ''},
        {'type': 'me', 'say': '我肚子饿了，姐姐――'},
        {'type': 'line', 'who': 'miyuki', 'say': '多吃多吃啊，小修――', 'expr': 'smile', 'action': ''},
        {'type': 'free', 'prompt': '老屋的日常。你想对姐姐说什么？（试试：来陪我打扑克 / 一起去堆雪人 / 姐姐晚安……）', 'chips': ['来陪我打扑克吧', '一起去堆雪人嘛', '姐姐，晚安']},
        {'type': 'narration', 'text': '门前堆了两个雪人，戴着水桶帽，相依相偎。屋檐下，我们的呼气在冷冽的空气中变成白色，又缓缓消散。'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修，晚安――', 'expr': 'smile', 'action': ''},
        {'type': 'me', 'say': '晚安，姐姐――'},
        {'type': 'effect', 'flags': {'daily_life': True}, 'daily_inc': True, 'affection': 2},
    ],
}

# ================================================================ P9 再量身高
SCENES['P9'] = {
    'title': 'P9 · 柱上的痕',
    'location': 'oldhouse_in',
    'time': 'night',
    'bg': 'bg_oldhouse_room_night.png',
    'beats': [
        {'type': 'narration', 'text': '明天，我便不得不回到东京了。我闷闷不乐地收拾着行李。要带回去的行李，比以前还要沉重。'},
        {'type': 'line', 'who': 'miyuki', 'say': '呐，小修。还记得那根柱吗？', 'expr': 'normal', 'action': '（姐姐所指的，是壁龛边那厚厚的柱。那根柱。我还记得。上面刻着一道浅浅的痕）'},
        {'type': 'me', 'say': '我想起来了。都过了三年了……姐姐'},
        {'type': 'narration', 'text': '姐姐的脸上，欣喜地绽开了笑容。'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修还记得呢。那姐姐再为你量一次身高', 'expr': 'smile', 'action': '（她和三年前一样，牵着我走到了柱的前面）'},
        {'type': 'narration', 'text': '那柱上刻着的痕，如今的位置，比我的肩头还要低。那落差，是我们未能达成约定的三年时光。有去年，也有前年。'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修……长高了不少呢', 'expr': 'smile', 'action': ''},
        {'type': 'choice', 'options': [
            {'label': '没能让姐姐每年都量一下啊，抱歉', 'intents': ['apology'], 'affection': 3, 'axis': {'bond': 2}},
            {'label': '（沉默地看着旧痕）', 'intents': ['smalltalk'], 'affection': 1, 'axis': {'bond': 1}},
        ]},
        {'type': 'line', 'who': 'miyuki', 'say': '小修，不要在意啦', 'expr': 'smile', 'action': ''},
        {'type': 'me', 'say': '但是，明年我一定会回来的'},
        {'type': 'narration', 'text': '听到我说的话，她无言地点了点头。如今，我们已经不需要再勾小指了。这约定，一定会实现。'},
        {'type': 'line', 'who': 'miyuki', 'say': '明年，小修也该升学了吧', 'expr': 'normal', 'action': ''},
        {'type': 'me', 'say': '姐姐也是啊'},
        {'type': 'line', 'who': 'miyuki', 'say': '……没错', 'expr': 'normal', 'action': '（姐姐与我，年龄相差两岁）'},
        {'type': 'me', 'say': '对了，姐姐什么时候念书啊？不趁着寒假的时候好好念书，真的没关系吗？'},
        {'type': 'line', 'who': 'miyuki', 'say': '不用担心念书的事啦', 'expr': 'normal', 'action': ''},
        {'type': 'me', 'say': '那可不行。姐姐不要总是关心我了，要好好念书……不然将来可是会变得不幸啊？'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修，人要得到幸福，可不是只能通过一种方法的', 'expr': 'normal', 'action': ''},
        {'type': 'line', 'who': 'miyuki', 'say': '对姐姐来说，小修能够回到这里陪姐姐，那就是最幸福的事了哦？', 'expr': 'smile', 'action': '（我一时无法反驳。羞得连耳根都红了，无言以对）'},
        {'type': 'line', 'who': 'miyuki', 'say': '所以啊，明年也一定……', 'expr': 'smile', 'action': ''},
        {'type': 'me', 'say': '嗯，一定'},
        {'type': 'narration', 'text': '那一晚，我们在同一个房间里面，并肩而眠。'},
        {'type': 'effect', 'flags': {'height_remarked': True}, 'affection': 4},
    ],
}

# ================================================================ P10 离别晨
SCENES['P10'] = {
    'title': 'P10 · 齐刘海',
    'location': 'oldhouse_front',
    'time': 'day',
    'bg': 'bg_courtyard.png',
    'beats': [
        {'type': 'narration', 'text': '天亮了。当我睁开眼睛时，姐姐已经起床，叠好了被子。厨房传来使用刀具的声音，安静的旋律，让人心安稳沉静——姐姐在为我准备早餐。对于这次归省而言，这是最后的早餐了。'},
        {'type': 'narration', 'text': '我与姐姐走出了家门，白雪纷纷扑面而来。'},
        {'type': 'line', 'who': 'miyuki', 'say': '雪人好像脏了', 'expr': 'normal', 'action': '（姐姐说的，是装点在门前的那两个雪人。雪有些化掉了，所以它们也变得不成样子）'},
        {'type': 'narration', 'text': '庭院中种植着几棵老树。其中格外苍老的那一棵，是在我出生之前便已种植在这个庭院中的樱花树吧。我很久都没见过这棵树上开出美丽的樱花了。如今，只有素净的白雪在光秃的枝头上盛开。'},
        {'type': 'me', 'say': '姐姐。这棵樱花树，春天到了会开花吗？'},
        {'type': 'line', 'who': 'miyuki', 'say': '……哎', 'expr': 'surprise', 'action': ''},
        {'type': 'line', 'who': 'miyuki', 'say': '会开花啊，开花时好漂亮的', 'expr': 'smile', 'action': ''},
        {'type': 'me', 'say': '是吗'},
        {'type': 'narration', 'text': '这里直到如今都没有变，我很开心。我顺手捡起了正好落在脚下的一根树枝。'},
        {'type': 'line', 'who': 'miyuki', 'say': '？', 'expr': 'surprise', 'action': '（姐姐有些不可思议地，在一旁观望着我）'},
        {'type': 'me', 'say': '这样就好了'},
        {'type': 'narration', 'text': '我用树枝，在雪人的头上画了一条线。在靠近额头的地方画了一条横线，然后在太阳穴的旁边也画了几条。这么一来，雪人又恢复了原本的样貌。'},
        {'type': 'cg', 'img': 'cg07.png'},
        {'type': 'narration', 'text': '雪人留着齐刘海的头型。和姐姐的样貌一摸一样。'},
        {'type': 'line', 'who': 'miyuki', 'say': '……嘛', 'expr': 'smile', 'action': '（姐姐这时才反应过来，我这样做想表达什么。她弯起嘴角，露出了一抹微笑——那是看起来非常开心，而又有些害羞的微笑。这一定是，我们正式成为姐弟的仪式）'},
        {'type': 'narration', 'text': '她真的很开心，就连奔向车站的脚步，也变得轻快了起来。'},
        {'type': 'effect', 'location': 'station', 'bg': 'bg_station_day.png'},
        {'type': 'narration', 'text': '无论何时来，站台上都是空空荡荡。静悄悄地，四下无人。这个地方，仿佛不属于现实一般。我在站台上伫立着，就好像立于梦境与现实相连的栈桥上。'},
        {'type': 'line', 'who': 'miyuki', 'say': '保重身体哦，小修', 'expr': 'smile', 'action': ''},
        {'type': 'choice', 'options': [
            {'label': '嗯，姐姐也是', 'intents': ['farewell'], 'affection': 2, 'axis': {'bond': 2}},
            {'label': '（想说的话终究没有说完整）', 'intents': ['farewell'], 'affection': 1, 'axis': {'bond': 1, 'worldly': 1}},
        ]},
        {'type': 'narration', 'text': '寥寥数语过后。随后，我走进了车厢中。伴着咣当咣当的声响，列车开始启动，缓缓地开出了安静的站台。姐姐的身影越来越远。'},
        {'type': 'narration', 'text': '如今我仅仅是望着她，便无法抑制涌动的心潮。这不过是错觉——我如此劝诫着自己。姐姐是我唯一的家人，我不应对她抱有多余的感情。忽然，我的胸口一阵绞痛。'},
        {'type': 'narration', 'text': '我第一次期盼，能够早一些回到那栋老屋。而前路依旧遥遥。灰色的连绵山峰，伫立在漫天飞雪的纱幕另一头。'},
        {'type': 'narration', 'text': '——田间小路上，并排留下了两行黑色的足迹。她那乌黑的美丽长发，在夹杂着飞雪的寒风中飘扬。'},
        {'type': 'narration', 'text': '不觉间，并肩而行的二人中，一人停下了脚步，用漆黑的眼瞳遥望着远方。在那漆黑眼瞳望向的另一边，是远方那白雪皑皑的连亘山峰。仿佛那里有人在等待着她一般。'},
        {'type': 'narration', 'text': '而那个少女，只是安静地凝视着那片群山。'},
        {'type': 'effect', 'flags': {'left_again': True}, 'affection': 3},
    ],
}

# ================================================================ P0 终章·雪原
SCENES['P0'] = {
    'title': 'P0 · 白之彼方',
    'location': 'blizzard',
    'time': 'evening',
    'bg': 'bg_mountains_blizzard.png',
    'beats': [
        {'type': 'narration', 'text': '我依稀听到一阵咏叹。这一定是我的错觉吧。除了我，这里明明没有旁人。'},
        {'type': 'narration', 'text': '据说，群山有奇异的魔性。很久以前，这绵绵群山，并非人类所拥有的土地。而是被称为异界，为人所恐惧。即使是在种种传说褪去了神秘色彩的现代，这群山，每年也会吞噬无数的生命。'},
        {'type': 'narration', 'text': '我无数次地交替着迈出脚步，登山靴下面，凝固成块的雪被踩得沙沙作响。刚刚落下的新雪上，留下了一串黑色的足迹。幽幽深山中，这份无垢的纯白，就这样被我一路踏过，刻下了不可抹去的污迹。'},
        {'type': 'me', 'say': '……在充满了虚伪谎言的世间，没有比这里更接近世界真实面貌的地方了'},
        {'type': 'narration', 'text': '曾有位登山家如此说道。我想，现在的我略微理解了他所说的话。我必须要前行。必须要到达我的目的地——到父亲和母亲那里去。到二人等待着我的地方去。'},
        {'type': 'narration', 'text': '深广的静寂，像是将一切都吞没了。无论是温度，光线，声音，时间。甚至是生命。天空变得阴沉下来。如果这里刮起了暴风雪……面对自己的预测，比寒气还要冰冷的感觉爬上了我的背脊。'},
        {'type': 'narration', 'text': '忽然，一阵风呼啸而过。卷起无数飞雪。纷纷扬起的雪花，遮住了我的视线。我急忙用一只手挡住了脸，屏息静气。'},
        {'type': 'cg', 'img': 'cg_snow.png'},
        {'type': 'narration', 'text': '——好像那边有人。在茫茫飞雪的另一边，伫立着一个朦胧的身影。'},
        {'type': 'cg', 'img': 'cg_yukihime.png', 'caption': '雪女'},
        {'type': 'narration', 'text': '那白色的身影，伫立在雪原中。使得我毛骨悚然。那是一个女人。她的肌肤如雪般洁净，穿着白色的和服。长发随着山风飘扬飞舞。那孤独而又冰冷、摄人心魄的、美丽无瑕的身影――是雪女。'},
        {'type': 'me', 'say': '――――啊'},
        {'type': 'narration', 'text': '此时，那个让人不由得浮想联翩的纯白身影，慢慢地转身向我回望。她的脸色很苍白。那是一张，我比任何人都要熟知的面庞。'},
        {'type': 'me', 'say': '…………姐姐'},
        {'type': 'narration', 'text': '朦胧的身影伫立在风雪之中，她望着我的眼神，却有些怅然。只有朱唇微微地轻启。'},
        {'type': 'line', 'who': 'yukihime', 'say': '修二――――', 'expr': 'white', 'action': ''},
        {'type': 'me', 'say': '姐……'},
        {'type': 'narration', 'text': '我不由得移开了视线。就在这个瞬间，一阵雪崩的声音惊醒了我。'},
        {'type': 'me', 'say': '啊…………'},
        {'type': 'narration', 'text': '飞雪停歇，另一边空空如也。那个人消失得无影无踪。都随着风雪停歇而消失了，和她出现时一样猝然。她，消失了……她真的消失了吗。还是说，她从一开始，就不曾真正地存在过。'},
        {'type': 'narration', 'text': '我感到身上的体温渐渐地下降。巍巍群山，茫茫雪原。在这个群山环绕的地方，我不禁感叹，自己是那么的渺小。'},
        {'type': 'narration', 'text': '我鼓起快要耗尽的气力，抬起了如同灌了铅一般沉重的双腿，向前迈进。我必须要前进，必须要抵达目的地。到父亲和母亲那里去。到二人等待着我的那个地方去。那个地方，已经不远了。'},
        {'type': 'effect', 'flags': {'finale': True}},
    ],
}

PHASE_ORDER = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10',
               'P11', 'P12B', 'P12M', 'E_STAY', 'E_SPRING', 'E_FAR', 'E_TOKYO', 'P0']

# ================================================================ P11 一年后的岔路（D0）
SCENES['P11'] = {
    'title': 'P11 · 一年后的岔路',
    'location': 'station',
    'time': 'day',
    'bg': 'bg_station_day.png',
    'beats': [
        {'type': 'narration', 'text': '一年又过去了。期中与期末、东京的教室与宿舍，把日历撕得飞快。寒假的第一天，我提着行李，站上了上山站的站台。站台照旧空无一人。'},
        {'type': 'narration', 'text': '她没有来。也许正在老屋的炉边等着，也许正站在檐廊下听雪。这一次，没有人牵我的手——路，要自己选了。'},
        {'type': 'branch_text', 'cases': [
            {'cond': 'axis:obsession>=35',
             'text': '（行李的最底层，压着一张手绘的地图。山麓、搜救队当年走过的路线、父亲笔记里提到过的岔口……这一年里，我查过太多东西。）'},
            {'cond': 'default',
             'text': '（山在视野的尽头白着。我告诉自己，只是看看而已。）'},
        ]},
        {'type': 'choice', 'options': [
            {'label': '先去群山——去父亲和母亲所在的地方', 'intents': ['ask_parents'], 'requires': 'axis:obsession>=35',
             'flag': 'chose_mountains', 'axis': {'obsession': 5},
             'fail_flag': 'chose_return',
             'fail_text': '（脚迈向站台的另一头，却像陷进雪里一样沉。装备、体力、理由……都还没有准备好。我终于承认——现在的自己，还没有踏进那片白色的资格。）'},
            {'label': '回到雪国——回到姐姐身边', 'intents': ['promise_return'], 'flag': 'chose_return', 'axis': {'bond': 3}},
            {'label': '今年，就留在东京吧', 'intents': ['refuse'], 'requires': 'axis:worldly>=35',
             'flag': 'stayed_tokyo', 'axis': {'worldly': 3},
             'fail_flag': 'chose_return',
             'fail_text': '（话是这么说。可提笔写假期安排的时候，笔尖在「雪国」两个字上停了很久。等到回过神来，列车已经载着我，走在回去的路上。）'},
        ]},
        {'type': 'effect', 'flags': {'fork_done': True}},
    ],
}

# ================================================================ P12M 雪径（入山线）
SCENES['P12M'] = {
    'title': 'P12M · 雪径',
    'location': 'mountains',
    'time': 'evening',
    'bg': 'bg_mountain_path.png',
    'beats': [
        {'type': 'narration', 'text': '我没有先去老屋。把行李寄存在车站的柜子里，只背了一个轻包——地图、绳索、手电、三天的口粮。出发前给鸟羽老人挂了个电话，铃响到第七声，我挂断了。有些话一旦说出口，就会被人拦住。'},
        {'type': 'me', 'say': '……我出发了'},
        {'type': 'narration', 'text': '（对不起，姐姐。拉了勾的约定，我要先失约了。——等我把该接的人接回来，就回去向你赔罪。）'},
        {'type': 'narration', 'text': '山麓的雪没过膝盖。每一步都要先把腿从雪里拔出来。地图上的岔口和实地对不上——父亲笔记里的字迹，到这里就停了。'},
        {'type': 'narration', 'text': '不知走了多久。天色沉了下来，风从山脊上滚落，卷起地上的新雪。白色的飞沫遮住了视野。远处，有咏叹声一样的东西，混在风里。'},
        {'type': 'branch_text', 'cases': [
            {'cond': 'flag:parents_belief',
             'text': '（他们在呼唤。这一年里我终于敢承认——那不是幻听。是呼唤。）'},
            {'cond': 'default',
             'text': '（风里有声音。像呼唤，又只是风。）'},
        ]},
        {'type': 'narration', 'text': '雪原的深处，伫立着一个白色的身影。'},
        {'type': 'me', 'say': '――还有人？'},
        {'type': 'narration', 'text': '那身影转过来的弧度，那么缓慢，又那么熟悉。我的心跳漏了一拍——那张脸，我比任何人都要熟识。'},
        {'type': 'effect', 'location': 'blizzard', 'bg': 'bg_mountains_blizzard.png', 'axis': {'obsession': 5}},
    ],
}

# ================================================================ P12B 幸福之问（归省线·D1）
SCENES['P12B'] = {
    'title': 'P12B · 田间小路',
    'location': 'fields',
    'time': 'day',
    'bg': 'bg_mountains.png',
    'beats': [
        {'type': 'narration', 'text': '老屋的炉火、清雪、扑克、并肩而眠——几天的归省像一场太短的梦。回东京的日子又到了。深雪送我，走在这条田间小路上。雪把两边的田野盖成一片白，两行足迹在身后排开。'},
        {'type': 'line', 'who': 'miyuki', 'say': '今年，是小修自己回来的呢', 'expr': 'smile', 'action': '（她走在我旁边，脚步轻快。这话里有一点小小的得意）'},
        {'type': 'me', 'say': '……嗯。我自己回来的'},
        {'type': 'narration', 'text': '风从群山的方向吹过来。她忽然停下脚步，用漆黑的眼瞳望着我。'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修――', 'expr': 'smile', 'action': ''},
        {'type': 'line', 'who': 'miyuki', 'say': '觉得现在幸福吗……？', 'expr': 'normal', 'action': '（突如其来的提问。她安静地等着，不催促）'},
        {'type': 'free', 'prompt': '（原文里没能回答的那句话，由你来回答。说出真心话——它会决定故事的走向）', 'chips': ['和你在一起很幸福', '望着群山说不出话', '……']},
        {'type': 'choice', 'options': [
            {'label': '那就，留在这里——今年哪儿也不去了', 'intents': ['ask_stay'], 'requires': 'axis:bond>=50',
             'flag': 'chose_stay', 'axis': {'bond': 5}, 'fail_flag': 'stay_promise_failed',
             'fail_text': '「留下来」三个字在舌尖上化掉了，像雪落在手心。深雪轻轻摇头，笑容一如往常：「傻瓜。小修的教室在东京哦。……不过，谢谢你。」'},
            {'label': '春天，樱花开的时候，我再来见你', 'intents': ['promise_return'], 'requires': ['axis:bond>=50', 'axis:obsession<35'],
             'flag': 'chose_spring', 'axis': {'bond': 3}, 'fail_flag': 'spring_promise_failed',
             'fail_text': '「春天」两个字出口的时候，她的笑容淡了一瞬。她朝群山的方向望了一眼，什么也没说。而我，没能把「一定」说出口。'},
            {'label': '（话终究没有说完整）', 'intents': ['smalltalk'], 'flag': 'said_nothing'},
        ]},
        {'type': 'effect', 'flags': {'happiness_asked': True}, 'axis': {'bond': 1}},
    ],
}

# ================================================================ E_STAY 留守线（END_STAY）
SCENES['E_STAY'] = {
    'title': 'E · 炉火与春讯',
    'location': 'oldhouse_in',
    'time': 'evening',
    'bg': 'bg_oldhouse_room.png',
    'beats': [
        {'type': 'narration', 'text': '我在路口转过身，朝老屋走回去。深雪跟了上来，与我并肩。谁都没有说话，可脚步越来越快，最后几乎是小跑着，推开了那扇门。'},
        {'type': 'line', 'who': 'miyuki', 'say': '姐姐去添炭。小修去把烟囱上的雪拍一拍——今晚，要多煮一个人的饭了哦', 'expr': 'smile', 'action': ''},
        {'type': 'cg', 'img': 'cg_stay.png'},
        {'type': 'narration', 'text': '炉火重新旺了起来。窗外的雪声被隔得很远。晚饭是白粥和腌菜，热气把彼此的脸都熏得模糊。'},
        {'type': 'free', 'prompt': '（留下的第一个夜晚。你想对姐姐说什么？）', 'chips': ['姐姐，晚安', '春天来了会怎样？', '……']},
        {'type': 'narration', 'text': '夜里，我们隔着被炉说话，说到灯芯结花。她忽然安静了一会儿。'},
        {'type': 'line', 'who': 'miyuki', 'say': '呐，小修。春天来的时候……你还会在吗？', 'expr': 'normal', 'action': '（她问得很轻，像怕惊动什么）'},
        {'type': 'choice', 'options': [
            {'label': '在。哪儿都不去', 'flag': 'stay_confirmed', 'axis': {'bond': 3}},
            {'label': '……在。至少，到开学', 'axis': {'worldly': 2, 'bond': 1}},
        ]},
        {'type': 'narration', 'text': '我在雪国住了下来。清雪、泡澡、做饭、扑克——老屋的循环里，从此多出一个不会离开的位置。只是有时，镇上的人会在檐廊下多看我们两眼；只是偶尔，风从山那边吹过来的时候，她的笑容会停一下，像在听什么。'},
        {'type': 'narration', 'text': '亲戚那边总要有个说法，东京的学籍也是。……可那是春天以后的事了。今晚，先把饭煮上。'},
        {'type': 'narration', 'text': '雪一直下。春天，还没有来。'},
        {'type': 'effect', 'axis': {'bond': 2}},
    ],
}

# ================================================================ E_SPRING 真结局（END_SPRING）
SCENES['E_SPRING'] = {
    'title': 'E · 等到花开',
    'location': 'fields',
    'time': 'day',
    'bg': 'bg_fields_spring.png',
    'beats': [
        {'type': 'narration', 'text': '东京的春天来得很吵。开学、大扫除、粉笔灰。我把那个约定折好，放进内袋，等假期的列车。'},
        {'type': 'narration', 'text': '春假。我又一次踏上上山站。这一次，站台上吹的风是软的。雪水沿着铁轨的形状，淌成两条细细的溪流。'},
        {'type': 'narration', 'text': '田间小路卸下了它的白色。田埂露出黑土，水洼里晃着天光。路的尽头，老屋的院墙上探出一角粉色——'},
        {'type': 'me', 'say': '…………开了'},
        {'type': 'effect', 'location': 'courtyard', 'bg': 'bg_courtyard_spring.png'},
        {'type': 'cg', 'img': 'cg_spring.png'},
        {'type': 'narration', 'text': '樱花开了。那棵比我更老的老树，满枝都是浅色的花，开得没有一点犹豫。树下，站着一个比冬天里更明亮的身影。'},
        {'type': 'line', 'who': 'miyuki', 'say': '欢迎回来哦，小修', 'expr': 'spring',
         'action': '（她站在樱花树下。春装轻盈，发梢被春风轻轻掀起）',
         'cast': ['shuuji', 'miyuki']},
        {'type': 'me', 'say': '为什么……春天，你也在？'},
        {'type': 'line', 'who': 'miyuki', 'say': '因为约好了呀', 'expr': 'smile', 'action': '（她说得理所当然，像在说雪是白的）'},
        {'type': 'narration', 'text': '门口的两个雪人已经化得只剩矮矮的雪堆，可额头上的那一道，还看得出形状。我蹲下去，用指尖把齐刘海又描了一遍。'},
        {'type': 'narration', 'text': '「这样就好了。」——去年冬天，是我这样说的。今年，她替我说了。'},
        {'type': 'line', 'who': 'miyuki', 'say': '嗯。这样就好了', 'expr': 'smile', 'action': ''},
        {'type': 'effect', 'flags': {'accepted_sister': True}, 'axis': {'obsession': -10}},
        {'type': 'narration', 'text': '花瓣落进她的发间，分不清哪个是白，哪个是粉。群山还在视野的尽头白着——但今天的我，先看花。'},
    ],
}

# ================================================================ E_FAR 原作向（END_FAR）
SCENES['E_FAR'] = {
    'title': 'E · 两行足迹',
    'location': 'fields',
    'time': 'day',
    'bg': 'bg_mountains.png',
    'beats': [
        {'type': 'narration', 'text': '路口。一条路通向车站，一条路通回老屋。我朝车站的方向，迈开了脚步。'},
        {'type': 'line', 'who': 'miyuki', 'say': '我送你', 'expr': 'smile', 'action': '（她自然地走在我旁边，像第一次送站时那样）'},
        {'type': 'narration', 'text': '田间小路上，并排留下了两行黑色的足迹。雪还在下，把来路和去路都慢慢抹平。'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修，不用回头也是知道的哦', 'expr': 'smile', 'action': '（她在站台上，像每一次那样朝我挥手）'},
        {'type': 'me', 'say': '嗯。……明年'},
        {'type': 'branch_text', 'cases': [
            {'cond': 'flag:spring_promise_failed',
             'text': '「春天」——这个约定，我没能守住。期末、亲戚、生活里连绵不断的琐事，把三月碾了过去。等我能再站上那座站台时，已经是冬天。她还是那样站在老屋门口，笑着说「欢迎回家」。好像迟到的从来不是我，只是雪。'},
            {'cond': 'flag:stay_promise_failed',
             'text': '「留下来」——我把这三个字咽了回去。东京的教室里，我偶尔会想起那天路口的炉火味。可想起归想起，列车依旧准点。'},
            {'cond': 'default',
             'text': '那句回答，我至今没能说完整。她大概早就习惯了——她等着的，从来都是一个会迟到的人。'},
        ]},
        {'type': 'cg', 'img': 'cg08.png'},
        {'type': 'cg', 'img': 'cg_far.png'},
        {'type': 'narration', 'text': '列车开动。她的身影越来越小，最后停在原地——朝着我看不见的、群山的方向。仿佛那里，有什么人在等待着她。'},
        {'type': 'narration', 'text': '而那句提问的答案，我把它和车票收在一起。总有一天，我会带着答案回来的。一定。'},
        {'type': 'effect', 'axis': {'bond': 1}},
    ],
}

# ================================================================ E_TOKYO 留京线（并入 END_FAR）
SCENES['E_TOKYO'] = {
    'title': 'E · 东来的雪',
    'location': 'town_street',
    'time': 'night',
    'bg': 'bg_tokyo.png',
    'beats': [
        {'type': 'narration', 'text': '「今年就留在东京吧」——说出这句话的时候，我听见自己的声音，平静得像在念别人的课程表。'},
        {'type': 'narration', 'text': '假期过去了。然后是下一个学期，下一个冬天。雪国的消息断了——没有地址，没有电话，只有一个我没能遵守的约定。'},
        {'type': 'narration', 'text': '唯一从那边寄来的东西，是一座停摆的挂钟。亲戚收拾老屋时寄来的，说「反正你也不回去」。指针停在四时四十九分。我把它挂在公寓的墙上。它不走，可我每天都会看它。'},
        {'type': 'narration', 'text': '有年冬天，东京下了很大的雪。站台人潮汹涌，我在人群里忽然停下脚步——因为有个撑伞的身影，侧脸白得像雪。我追了两步，又站住。不会是她。她在雪国。她一直都在雪国，等一个会迟到的人。'},
        {'type': 'me', 'say': '……明年。明年一定'},
        {'type': 'narration', 'text': '这句话，我对自己说了很多年。'},
    ],
}
