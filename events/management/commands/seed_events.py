from datetime import time, timedelta
from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Category, Event

# DESCRIPTION GENERATORS

# BASE CODE BY MYSELF, FULLY IMPLEMENTED BY CHATGPT

THEME_DESCRIPTION_DATA = {

    "walking_tour": {
        "category": "Adventure",
        "openings": [
            "Step away from the usual routine and discover the stories hidden around the town.",
            "Spend an afternoon exploring familiar streets from a completely different perspective.",
            "Take a leisurely walk through the town while uncovering some of the stories hiding in plain sight.",
        ],
        "activities": [
            "Follow an experienced local guide through historic streets, forgotten corners, and landmarks that are easy to overlook.",
            "Discover unusual stories, local characters, and fascinating details that have shaped the area over the years.",
            "Explore the streets while hearing stories about the people, buildings, and events that helped shape the town.",
        ],
        "details": [
            "The relaxed pace gives you plenty of time to look around, ask questions, and discover something you might otherwise have walked straight past.",
            "Whether you're new to the area or have lived here for years, there's always another story waiting to be uncovered.",
            "It's a great way to see the town differently while picking up a few stories to share afterwards.",
        ],
        "closings": [
            "Bring comfortable shoes, a little curiosity, and let the town tell its story.",
            "Come along, take your time, and discover what you've been walking past all this time.",
        ],
    },

    "kayaking": {
        "category": "Adventure",
        "openings": [
            "Get out on the water for an active few hours of paddling, fresh air, and exploration.",
            "Swap the pavement for the water and discover the local landscape from a completely different angle.",
            "Grab a paddle and get ready for an outdoor adventure with plenty of fresh air and movement.",
        ],
        "activities": [
            "Learn the basics of kayaking before heading out onto the water with guidance from an experienced instructor.",
            "You'll practise paddling techniques, steering, and basic safety before exploring the waterway together.",
            "The session combines practical instruction with plenty of time to enjoy the water and surrounding scenery.",
        ],
        "details": [
            "No previous kayaking experience is required, and you'll be supported throughout the session.",
            "Expect a mixture of practical learning, gentle exploration, and the occasional splash.",
            "It's a relaxed introduction to kayaking with plenty of opportunity to build confidence on the water.",
        ],
        "closings": [
            "Bring suitable outdoor clothing and get ready to make a splash.",
            "Grab your paddle, leave the shore behind, and enjoy the adventure.",
        ],
    },

    "hiking": {
        "category": "Adventure",
        "openings": [
            "Leave the everyday behind and spend some time exploring the great outdoors.",
            "Get your walking boots ready for a scenic adventure through some of the area's most beautiful surroundings.",
            "Enjoy a few hours of fresh air, open scenery, and plenty of opportunity to explore.",
        ],
        "activities": [
            "Follow a carefully planned route through woodland, open countryside, and scenic viewpoints.",
            "An experienced guide will lead the way while sharing local stories, landmarks, and points of interest.",
            "The route combines gentle walking with some rewarding viewpoints and plenty of opportunities to stop and take in the scenery.",
        ],
        "details": [
            "The pace is designed to be enjoyable rather than competitive, giving everyone time to appreciate the surroundings.",
            "It's ideal for anyone who enjoys walking, photography, nature, or simply escaping the usual routine for a few hours.",
            "Expect a mixture of conversation, fresh air, scenery, and the occasional well-earned rest.",
        ],
        "closings": [
            "Bring comfortable footwear, plenty of water, and your sense of adventure.",
            "Lace up your boots and come see where the trail leads.",
        ],
    },

    "climbing": {
        "category": "Adventure",
        "openings": [
            "Challenge yourself to try something new with an introduction to indoor climbing.",
            "Put your strength, balance, and problem-solving skills to the test.",
            "Ready to get off the ground? This climbing session is designed to give beginners a chance to have a go.",
        ],
        "activities": [
            "Learn the fundamentals of climbing, including movement, balance, and basic safety techniques.",
            "Experienced instructors will introduce you to the walls before helping you tackle a range of beginner-friendly routes.",
            "Work your way through different climbing challenges while learning how to approach routes with confidence.",
        ],
        "details": [
            "No previous experience is required, and routes can be adapted to suit different confidence levels.",
            "It's as much about figuring out the puzzle of each route as it is about reaching the top.",
            "Expect encouragement, a few challenging moments, and plenty of reasons to celebrate when you reach the finish.",
        ],
        "closings": [
            "Give it a go, trust your feet, and see how high you can get.",
            "Climb at your own pace and discover just how addictive reaching the top can be.",
        ],
    },

    "orienteering": {
        "category": "Adventure",
        "openings": [
            "Put your navigation skills to the test with an outdoor challenge built around exploration.",
            "Grab a map, find your bearings, and prepare for an adventure where the route is up to you.",
            "Think you know your way around? It's time to put those navigation skills to work.",
        ],
        "activities": [
            "Work your way between checkpoints using maps, clues, and your own sense of direction.",
            "Navigate a series of checkpoints while deciding which route will get you there most effectively.",
            "Solve navigation challenges, discover hidden checkpoints, and work together to complete the course.",
        ],
        "details": [
            "The challenge can be approached at your own pace, making it suitable for beginners and experienced navigators alike.",
            "You'll need a mixture of observation, teamwork, and careful decision-making to find your way around.",
            "Getting slightly lost is all part of the fun, provided you eventually find your way back.",
        ],
        "closings": [
            "Bring your curiosity, keep your bearings, and see if you can find them all.",
            "Trust the map, watch the clues, and let the adventure begin.",
        ],
    },

    "pottery": {
        "category": "Arts & Culture",
        "openings": [
            "Discover the satisfying art of working with clay in this relaxed beginner-friendly pottery workshop.",
            "Spend an evening getting your hands dirty and discovering what you can create from a lump of clay.",
            "Take a break from the everyday and try your hand at the wonderfully tactile world of pottery.",
        ],
        "activities": [
            "Learn how to prepare and shape clay before experimenting with simple forms, textures, and decorative techniques.",
            "You'll be guided through the basics of pottery before getting plenty of time to create something of your own.",
            "Explore shaping, moulding, and decorating techniques while working towards your own handmade piece.",
        ],
        "details": [
            "An experienced potter will guide you through the process while leaving plenty of room for experimentation.",
            "There is no pressure to create a masterpiece, and beginners are encouraged to experiment and enjoy the process.",
            "You'll discover how surprisingly satisfying it can be to turn a simple piece of clay into something completely your own.",
        ],
        "closings": [
            "Come ready to experiment, get messy, and create something you can be proud of.",
            "Roll up your sleeves and see what your hands can make.",
        ],
    },

    "watercolour": {
        "category": "Arts & Culture",
        "openings": [
            "Slow things down and explore the gentle, expressive world of watercolour painting.",
            "Spend a relaxed afternoon discovering how colour, water, and brushwork can transform a blank page.",
            "Pick up a brush and explore the basics of watercolour in a friendly creative setting.",
        ],
        "activities": [
            "Learn about colour mixing, washes, layering, and simple brush techniques before creating your own piece.",
            "You'll work through a series of practical exercises before putting your new techniques together in a finished painting.",
            "Experiment with colour, texture, and water while learning how to create depth and atmosphere.",
        ],
        "details": [
            "The session is suitable for beginners and focuses on experimentation rather than perfection.",
            "You'll have plenty of guidance while still having the freedom to develop your own style.",
            "Expect a peaceful few hours of creativity, experimentation, and the occasional happy accident.",
        ],
        "closings": [
            "Bring your curiosity and let the colours do the talking.",
            "Pick up a brush and see where the afternoon takes you.",
        ],
    },

    "exhibition": {
        "category": "Arts & Culture",
        "openings": [
            "Spend an evening discovering local artists and the ideas behind their work.",
            "Step inside the gallery for an evening celebrating creativity from artists working in the local area.",
            "Explore a collection of work from emerging and established local creatives.",
        ],
        "activities": [
            "Take your time exploring paintings, photography, sculpture, and mixed-media pieces throughout the gallery.",
            "Meet artists, hear about their creative processes, and discover the stories behind selected works.",
            "Explore a varied collection while chatting with artists and fellow visitors about the work on display.",
        ],
        "details": [
            "The relaxed atmosphere makes it easy to browse at your own pace and ask questions along the way.",
            "Whether you know your art history or simply enjoy discovering something interesting, everyone is welcome.",
            "There is plenty to explore, with different styles and perspectives represented throughout the exhibition.",
        ],
        "closings": [
            "Take your time, enjoy the atmosphere, and see what catches your eye.",
            "Come curious and leave with a little more inspiration.",
        ],
    },

    "family_science": {
        "category": "Family",
        "openings": [
            "Bring the whole family along for a day of experiments, discoveries, and hands-on science.",
            "Get ready to explore the weird, wonderful, and surprisingly fun side of science.",
            "Curious minds of all ages can get involved with a day packed full of experiments and discoveries.",
        ],
        "activities": [
            "Try hands-on experiments, investigate fascinating scientific ideas, and discover how things work.",
            "Children can explore a range of interactive activities designed to make science exciting and accessible.",
            "Experiment, investigate, and test your theories through a mixture of demonstrations and practical activities.",
        ],
        "details": [
            "Activities are designed to encourage curiosity and give children plenty of opportunities to get involved.",
            "Grown-ups are encouraged to join in too, because there is no age limit on being fascinated by something exploding.",
            "The emphasis is on learning through doing, with plenty of opportunities to ask questions and make discoveries.",
        ],
        "closings": [
            "Bring your curiosity and prepare to discover something unexpected.",
            "Come ready to experiment, investigate, and perhaps say 'why does it do that?' several times.",
        ],
    },

    "treasure_hunt": {
        "category": "Family",
        "openings": [
            "Gather the family and get ready for an outdoor adventure packed with clues and discoveries.",
            "Put your detective skills to work with a family treasure hunt through the local area.",
            "Grab your team and prepare to solve clues, follow trails, and uncover hidden surprises.",
        ],
        "activities": [
            "Work together to solve clues, follow the trail, and discover hidden checkpoints along the route.",
            "Teams will need observation, teamwork, and a little creative thinking to make their way through the hunt.",
            "Follow riddles and clues through the area while working together to uncover the final location.",
        ],
        "details": [
            "The challenge is designed to be accessible to different ages, with everyone having a role to play.",
            "Expect plenty of teamwork, a few debates over which way to go, and hopefully a successful final discovery.",
            "It's a playful way to explore the area while keeping everyone involved.",
        ],
        "closings": [
            "Bring your best detective work and see if your team can crack the final clue.",
            "Gather your crew and let the hunt begin.",
        ],
    },

    "street_food": {
        "category": "Food & Drink",
        "openings": [
            "Come hungry and spend an evening exploring the flavours of the local street food scene.",
            "Take your taste buds on a journey through some of the area's best street food.",
            "Leave dinner plans at home and prepare for an evening built around great food and new flavours.",
        ],
        "activities": [
            "Visit a selection of independent food stalls while discovering dishes, ingredients, and the people behind them.",
            "Sample a variety of street food while exploring different cooking styles and flavours along the route.",
            "Your guide will introduce you to local favourites, hidden food spots, and dishes worth knowing about.",
        ],
        "details": [
            "There is plenty of opportunity to try something unfamiliar and discover a new favourite along the way.",
            "The relaxed pace means there is plenty of time to taste, chat, and enjoy the atmosphere.",
            "It's ideal for adventurous eaters and anyone who believes the best way to explore somewhere new is through its food.",
        ],
        "closings": [
            "Bring your appetite and prepare for a seriously tasty evening.",
            "Come hungry and leave with a list of places you'll want to visit again.",
        ],
    },

    "chocolate": {
        "category": "Food & Drink",
        "openings": [
            "Spend an indulgent few hours discovering the delicious world of handmade chocolate.",
            "If chocolate counts as a hobby, this is the workshop you've been waiting for.",
            "Get ready to learn, create, and sample your way through an afternoon of chocolate.",
        ],
        "activities": [
            "Learn about tempering, decorating, and working with chocolate before creating your own treats.",
            "You'll discover the basics of chocolate making and experiment with different flavours, textures, and decorations.",
            "Work with quality chocolate while learning techniques you can use again at home.",
        ],
        "details": [
            "The session is hands-on from start to finish, with plenty of opportunities to taste your creations along the way.",
            "No previous experience is required, although a healthy appreciation for chocolate is strongly recommended.",
            "You'll learn practical techniques while discovering just how much work goes into making those little things that mysteriously disappear from the cupboard.",
        ],
        "closings": [
            "Bring your sweet tooth and prepare to get wonderfully chocolatey.",
            "Come ready to learn, create, and probably eat a little more chocolate than planned.",
        ],
    },

    "pasta": {
        "category": "Food & Drink",
        "openings": [
            "Discover the surprisingly satisfying art of making fresh pasta from scratch.",
            "Forget the packet for an evening and learn how proper homemade pasta comes together.",
            "Roll up your sleeves and get ready for a hands-on journey into fresh pasta making.",
        ],
        "activities": [
            "Learn how to make pasta dough before shaping, cutting, and cooking your own fresh pasta.",
            "Work through the process from flour and eggs to finished pasta while learning practical kitchen techniques.",
            "You'll learn several simple techniques for preparing fresh pasta and turning it into a delicious meal.",
        ],
        "details": [
            "The workshop is relaxed and practical, with plenty of guidance available throughout.",
            "You'll have time to practise the techniques yourself before sitting down to enjoy the finished result.",
            "It's a great introduction to a skill that can easily become a favourite weekend kitchen project.",
        ],
        "closings": [
            "Come hungry and leave with a new appreciation for homemade pasta.",
            "Bring your appetite and prepare to get your hands covered in flour.",
        ],
    },

    "acoustic_music": {
        "category": "Music & Entertainment",
        "openings": [
            "Settle in for an evening of live music, warm atmosphere, and stripped-back performances.",
            "Spend the evening surrounded by acoustic music and an intimate atmosphere where the performers are never far away.",
            "Get comfortable for a relaxed night of live music, familiar songs, and original performances.",
        ],
        "activities": [
            "Enjoy talented local musicians performing acoustic versions of much-loved songs alongside original material.",
            "Hear local performers bring familiar favourites and original songs to life without the layers of a full production.",
            "Discover emerging musicians performing stripped-back sets in an intimate setting.",
        ],
        "details": [
            "Whether you're a dedicated music lover or simply looking for a chilled evening out, there's something special about hearing great songs performed up close and unplugged.",
            "The relaxed setting makes it easy to settle in, discover new artists, and enjoy the music without the noise of a huge venue.",
            "Expect a mixture of familiar favourites, original material, and the occasional song you didn't know you needed to hear live.",
        ],
        "closings": [
            "Grab a drink, get comfortable, and let the music take centre stage.",
            "Find yourself a seat, settle in, and enjoy the evening.",
        ],
    },

    "jazz": {
        "category": "Music & Entertainment",
        "openings": [
            "Spend the evening surrounded by live jazz, warm lighting, and an atmosphere made for taking things slowly.",
            "Settle in for an evening of live jazz performed beneath the stars.",
            "Enjoy an atmospheric night of live jazz with music, conversation, and plenty of room to relax.",
        ],
        "activities": [
            "A talented group of musicians will perform a mixture of classic standards and original arrangements.",
            "Enjoy live performances ranging from familiar jazz favourites to unexpected interpretations.",
            "The evening brings together experienced musicians for a varied set filled with improvisation and atmosphere.",
        ],
        "details": [
            "The outdoor setting gives the performance an extra sense of occasion without losing its relaxed feel.",
            "Whether you're already a jazz enthusiast or simply curious to hear something different, you're welcome.",
            "Expect expressive performances, plenty of atmosphere, and those wonderfully unpredictable moments that make live jazz special.",
        ],
        "closings": [
            "Bring a drink, find a comfortable spot, and let the music carry the evening.",
            "Settle in beneath the night sky and enjoy the show.",
        ],
    },

    "comedy": {
        "category": "Music & Entertainment",
        "openings": [
            "Prepare for an evening of stand-up comedy, questionable opinions, and hopefully very few awkward silences.",
            "Leave your serious face at home and settle in for a night of live comedy.",
            "Get comfortable and prepare to spend the evening laughing at people who have chosen comedy as a career.",
        ],
        "activities": [
            "A line-up of comedians will take to the stage with a mixture of observational humour, stories, and completely unpredictable material.",
            "Enjoy a varied line-up of performers bringing their latest material to the stage.",
            "The evening features several comedians, each bringing their own style and questionable life choices to the microphone.",
        ],
        "details": [
            "Expect plenty of laughs, the occasional audience interaction, and moments that probably shouldn't be repeated at work.",
            "The atmosphere is relaxed, informal, and designed for anyone who enjoys live comedy.",
            "Some jokes will be clever, some will be ridiculous, and at least one will probably make you wonder why you're laughing.",
        ],
        "closings": [
            "Grab a drink, take a seat, and prepare to laugh.",
            "Come along, get comfortable, and let someone else do the talking for a few hours.",
        ],
    },

    "pottery_workshop": {
        "category": "Workshops",
        "openings": [
            "Get your hands dirty and discover the satisfying process of creating something from clay.",
            "Spend a few relaxed hours learning the basics of pottery and creating something completely your own.",
            "Roll up your sleeves and explore the surprisingly therapeutic world of working with clay.",
        ],
        "activities": [
            "You'll learn how to prepare, shape, and decorate clay while working towards your own handmade piece.",
            "An experienced instructor will guide you through basic pottery techniques before giving you plenty of time to experiment.",
            "Learn practical techniques for shaping and decorating clay while developing your own ideas.",
        ],
        "details": [
            "The workshop is designed for beginners, so there is no expectation that you arrive knowing what you're doing.",
            "You'll have plenty of support while still having the freedom to experiment and see what happens.",
            "The emphasis is on learning through doing, with plenty of room for creativity and happy accidents.",
        ],
        "closings": [
            "Come ready to experiment, get messy, and make something memorable.",
            "Bring your curiosity and see what you can create with a little clay.",
        ],
    },

    "photography": {
        "category": "Workshops",
        "openings": [
            "Take your camera out into the world and discover how to see familiar places differently.",
            "Spend a morning learning how to turn everyday scenes into better photographs.",
            "Grab your camera and join us for a practical introduction to photography.",
        ],
        "activities": [
            "Learn about composition, lighting, framing, and camera settings before putting them into practice.",
            "You'll explore the local area while working through practical photography challenges.",
            "Experiment with different compositions and techniques while receiving guidance from an experienced photographer.",
        ],
        "details": [
            "The workshop focuses on practical skills that you can continue using long after the session ends.",
            "It's suitable for beginners and anyone who wants to become more confident behind the camera.",
            "You'll have plenty of opportunities to experiment rather than simply listen to technical explanations.",
        ],
        "closings": [
            "Bring your camera, comfortable shoes, and an eye for interesting details.",
            "Come ready to experiment and start seeing ordinary places differently.",
        ],
    },

    "woodworking": {
        "category": "Workshops",
        "openings": [
            "Spend a few hours working with real materials and learning the basics of woodworking.",
            "Step away from the screens and discover the satisfaction of making something from wood.",
            "Get hands-on with traditional woodworking techniques in this practical beginner-friendly workshop.",
        ],
        "activities": [
            "Learn how to safely use basic tools while measuring, cutting, shaping, and finishing your project.",
            "You'll be guided through the process from the first measurement to the final finishing touches.",
            "Discover practical techniques for working with wood before creating a small project of your own.",
        ],
        "details": [
            "The session is designed for beginners, with guidance available throughout the process.",
            "You'll learn at a comfortable pace while getting plenty of hands-on time with the materials.",
            "Expect sawdust, concentration, a few satisfying moments, and something you've actually made yourself.",
        ],
        "closings": [
            "Bring your curiosity and prepare to make some sawdust.",
            "Roll up your sleeves and see what you can build.",
        ],
    },

    "screen_printing": {
        "category": "Workshops",
        "openings": [
            "Discover the colourful world of screen printing in this practical creative workshop.",
            "Turn an idea into a printed design while learning the basics of screen printing.",
            "Get hands-on with ink, screens, and paper in a workshop designed for curious beginners.",
        ],
        "activities": [
            "Learn how screens are prepared before creating and printing your own simple designs.",
            "You'll explore the basic process of preparing artwork, applying ink, and producing a finished print.",
            "Experiment with layers, shapes, and colour while creating a small collection of your own prints.",
        ],
        "details": [
            "The workshop is beginner-friendly and focuses on experimentation rather than producing perfect results.",
            "You'll have plenty of guidance while still having room to develop your own designs.",
            "It's a wonderfully tactile process, and there is something very satisfying about lifting the screen to reveal the final print.",
        ],
        "closings": [
            "Come ready to get creative and leave with prints you've made yourself.",
            "Bring an idea, an open mind, and clothes you're not too precious about.",
        ],
    },

    "horror_experience": {
        "category": "Not For the Faint of Heart",
        "openings": [
            "Some evenings are better spent somewhere perfectly safe. This is not one of them.",
            "If ordinary nights out have stopped being interesting, perhaps it's time to try something a little darker.",
            "Tonight's experience is designed for people who enjoy being unsettled, surprised, and just a little bit nervous.",
            "Leave your sensible evening plans at home and prepare for something considerably less comfortable.",
        ],
        "activities": [
            "Explore dark corridors, forgotten rooms, and locations with stories that have never been properly explained.",
            "Follow the clues, investigate the surroundings, and discover what happened here after everyone else went home.",
            "Move through the location in a small group while strange sounds, unsettling discoveries, and unexpected moments unfold around you.",
            "Piece together the story as you explore, but don't expect every question to receive an answer.",
        ],
        "details": [
            "The experience is immersive, atmospheric, and deliberately unsettling, with plenty of moments designed to keep you guessing.",
            "Expect darkness, unexpected noises, and the occasional moment where you'll question whether you really saw something move.",
            "Nothing here is designed to leave you feeling completely comfortable, and that's rather the point.",
            "You may laugh, you may jump, and you may spend the journey home wondering whether that sound followed you.",
        ],
        "closings": [
            "Bring your courage, stay close to the group, and try not to look behind you.",
            "The lights are going down soon. You have been warned.",
            "If you're brave enough to enter, we'll see you on the other side.",
            "Come if you dare. Leave if you can.",
        ],
    },
}


def generate_theme_description(theme):
    """Generate a varied description based on the event's specific theme."""

    data = THEME_DESCRIPTION_DATA[theme]

    sentences = [
        random.choice(data["openings"]),
        random.choice(data["activities"]),
        random.choice(data["details"]),
    ]

    # Add a second detail sentence most of the time.
    if random.random() < 0.75:
        sentences.append(random.choice(data["details"]))

    # Add a closing sentence around half the time.
    if random.random() < 0.55:
        sentences.append(random.choice(data["closings"]))

    # Remove duplicate sentences while preserving order.
    result = []

    for sentence in sentences:
        if sentence not in result:
            result.append(sentence)

    return " ".join(result)


CATEGORY_DESCRIPTION_DATA = {
    "Adventure": {
        "openings": [
            "Get ready for an afternoon of exploration, fresh air, and something a little different.",
            "Step away from the usual routine and spend some time discovering somewhere new.",
            "Grab your gear and join us for an adventure packed with exploration, challenge, and plenty to see along the way.",
            "Discover a different side of the local area with an experience designed for curious explorers.",
            "Leave the ordinary behind and set out for an experience filled with fresh air, new surroundings, and a few surprises.",
        ],
        "activities": [
            "Explore scenic trails, hidden corners, and unusual landmarks while following an experienced local guide.",
            "Take part in a hands-on adventure that combines practical skills, exploration, and plenty of opportunities to get involved.",
            "Work your way through a series of challenges while discovering the landscape from a completely different perspective.",
            "Learn useful techniques along the way before putting them into practice during the main adventure.",
            "Follow the route at a relaxed pace while discovering stories, scenery, and places you might otherwise never notice.",
        ],
        "experiences": [
            "Whether you're a seasoned adventurer or simply looking for something different to do, there's plenty here to enjoy.",
            "It's an ideal way to spend a few hours outdoors while learning something new and meeting fellow explorers.",
            "Expect plenty of encouragement, a few challenges, and the occasional moment that makes the whole experience worthwhile.",
            "No previous experience is needed, just sensible footwear, a little curiosity, and a willingness to have a go.",
            "Come prepared to explore, get involved, and perhaps discover a new favourite way to spend an afternoon.",
        ],
        "closings": [
            "Bring your sense of adventure and see where the day takes you.",
            "Grab your gear, gather your friends, and get ready to explore.",
            "All that's left is to turn up, get involved, and enjoy the journey.",
            "The route is waiting. The only question is whether you're coming along.",
        ],
    },

    "Arts & Culture": {
        "openings": [
            "Spend some time surrounded by creativity, conversation, and plenty of inspiration.",
            "Step into a relaxed creative setting and discover something new.",
            "Enjoy an evening celebrating art, ideas, and the people who bring them to life.",
            "Take a break from the everyday and spend a few hours exploring creativity in all its forms.",
            "Discover local talent and creative ideas in an atmosphere designed for curiosity and conversation.",
        ],
        "activities": [
            "Explore different techniques, ideas, and styles while learning from experienced artists and performers.",
            "Enjoy a carefully selected collection of work while discovering the stories and inspiration behind it.",
            "Try your hand at creative techniques and experiment with different materials in a welcoming environment.",
            "Meet local creators, hear their stories, and discover the work that makes the local creative scene so interesting.",
            "Take your time exploring the work, asking questions, and discovering something that catches your imagination.",
        ],
        "experiences": [
            "Whether you're already passionate about the arts or simply curious to try something new, everyone is welcome.",
            "There's no need to be an expert, just bring an open mind and a willingness to experiment.",
            "It's a relaxed opportunity to discover new artists, techniques, and ideas without any pressure to be perfect.",
            "Expect plenty of inspiration, interesting conversations, and perhaps an idea or two to take home with you.",
            "The focus is on enjoying the experience, discovering something new, and letting your imagination do the rest.",
        ],
        "closings": [
            "Come along, settle in, and see where your creativity takes you.",
            "Bring your curiosity and leave with a little more inspiration than you arrived with.",
            "Take your time, enjoy the atmosphere, and let the creativity take centre stage.",
            "All that's required is curiosity. Everything else is provided.",
        ],
    },

    "Family": {
        "openings": [
            "Bring the whole family along for a day packed with fun, discovery, and plenty to get involved with.",
            "Looking for something everyone can enjoy? This family-friendly event has plenty to keep curious minds entertained.",
            "Gather the family and get ready for an experience designed to keep both children and grown-ups busy.",
            "Make some memories together with an event full of hands-on activities, discoveries, and plenty of laughs.",
            "Round up your little explorers and join us for a family adventure where everyone gets to take part.",
        ],
        "activities": [
            "Children can get involved with hands-on activities while grown-ups are encouraged to join in too.",
            "Explore, build, experiment, and discover something new together in a relaxed and welcoming environment.",
            "The session combines playful activities with opportunities to learn, create, and work together.",
            "There will be plenty of things to see, make, investigate, and enjoy throughout the session.",
            "Young explorers can get stuck into a range of activities designed to encourage curiosity and creativity.",
        ],
        "experiences": [
            "It's designed to be accessible for a range of ages, so nobody has to sit on the sidelines.",
            "Expect plenty of opportunities for teamwork, discovery, and the occasional wonderfully chaotic moment.",
            "No specialist knowledge is required, just enthusiasm and a willingness to get involved.",
            "It's the perfect chance to put the phones away for a while and enjoy some proper family time.",
            "Everyone gets something from the experience, whether they're there to learn, create, compete, or simply have fun.",
        ],
        "closings": [
            "Bring the family, get involved, and make an afternoon of it.",
            "All that's left is to bring your curiosity and your best team spirit.",
            "Come along ready to explore, laugh, and perhaps get a little messy.",
            "Gather everyone together and make some memories.",
        ],
    },

    "Food & Drink": {
        "openings": [
            "Come hungry and prepare to spend an evening discovering something delicious.",
            "Treat yourself to an experience built around good food, great flavours, and plenty of time to enjoy them.",
            "Take your taste buds somewhere new with an event designed for anyone who enjoys discovering good food.",
            "Food takes centre stage at this relaxed experience, with plenty of flavours to explore along the way.",
            "Settle in for an experience where good company and even better food are firmly on the menu.",
        ],
        "activities": [
            "Discover new flavours, learn from experienced food makers, and enjoy plenty of opportunities to sample the results.",
            "Explore ingredients, techniques, and dishes while getting an insight into the people and traditions behind them.",
            "Try a selection of carefully prepared dishes while discovering new combinations and local favourites.",
            "Get hands-on with the food, learning practical techniques before sitting down to enjoy what you've created.",
            "Work your way through a selection of flavours and dishes while learning a little more about how they're made.",
        ],
        "experiences": [
            "Whether you're a dedicated foodie or simply someone who enjoys a good meal, there's plenty to savour.",
            "Expect generous portions, interesting flavours, and plenty of opportunities to discover a new favourite.",
            "No expert knowledge is needed, just an appetite and a willingness to try something delicious.",
            "It's as much about the experience as the food, with plenty of time to relax, chat, and enjoy yourself.",
            "Come ready to taste, learn, and perhaps leave with a few ideas for your own kitchen.",
        ],
        "closings": [
            "Bring your appetite and let the kitchen do the rest.",
            "Come hungry, leave happy, and perhaps take a few new food ideas home with you.",
            "Grab a seat, enjoy the atmosphere, and prepare for a very tasty few hours.",
            "All that's left is to turn up hungry.",
        ],
    },

    "Music & Entertainment": {
        "openings": [
            "Settle in for an evening of live entertainment, warm atmosphere, and plenty to enjoy.",
            "Get comfortable and let the entertainment take centre stage for the evening.",
            "Spend the evening surrounded by live music, talented performers, and a relaxed atmosphere.",
            "Looking for a night out with a little more personality? This one has you covered.",
            "Leave the everyday behind and settle in for an evening built around great entertainment and good company.",
        ],
        "activities": [
            "Enjoy talented local performers bringing familiar favourites, original material, and unexpected surprises to the stage.",
            "Experience live performances in an intimate setting where the audience is close enough to feel part of the show.",
            "Expect a varied line-up of performers, plenty of energy, and an atmosphere that builds as the evening goes on.",
            "Hear familiar songs, discover new performers, and enjoy a night where the entertainment stays firmly in the spotlight.",
            "The evening brings together talented performers for a lively show designed to keep the room entertained from beginning to end.",
        ],
        "experiences": [
            "Whether you're a dedicated music lover or simply looking for a chilled evening out, there's something special about experiencing entertainment live.",
            "It's the perfect excuse to put your usual evening plans aside and enjoy something a little more memorable.",
            "Expect plenty of atmosphere, a few surprises, and moments you'll be talking about afterwards.",
            "Come for the performers, stay for the atmosphere, and enjoy an evening where the outside world can wait.",
            "There's no need to know every performer on the bill. Come along, discover something new, and enjoy the show.",
        ],
        "closings": [
            "Grab a drink, get comfortable, and let the show take centre stage.",
            "Find yourself a seat, settle in, and enjoy the evening.",
            "Bring your friends, grab a drink, and prepare for a great night out.",
            "All you need to bring is yourself and a willingness to enjoy the show.",
        ],
    },

    "Workshops": {
        "openings": [
            "Spend a few hours learning something new in a relaxed, hands-on workshop.",
            "Roll up your sleeves and discover a new skill in this friendly practical session.",
            "Fancy making something with your own hands? This workshop gives you the chance to learn, experiment, and create.",
            "Take a break from screens and spend some time learning a practical skill you can actually use.",
            "Discover the satisfaction of making something yourself in this relaxed and welcoming workshop.",
        ],
        "activities": [
            "You'll be guided through the basic techniques before getting plenty of time to practise them yourself.",
            "Learn the essential tools and techniques before putting them into practice on your own project.",
            "The session combines demonstrations with hands-on practice, giving you plenty of opportunities to experiment.",
            "Work through the process step by step while learning useful techniques from an experienced instructor.",
            "You'll have the chance to experiment with different materials and methods while creating something of your own.",
        ],
        "experiences": [
            "No previous experience is required, so beginners can relax and learn at their own pace.",
            "The atmosphere is friendly and informal, with plenty of guidance available whenever you need it.",
            "Expect a mixture of practical learning, experimentation, and the occasional happy accident.",
            "You'll leave with new skills, a better understanding of the craft, and something you've made yourself.",
            "The emphasis is on learning by doing, so don't worry about getting everything perfect on the first attempt.",
        ],
        "closings": [
            "Come along, get your hands dirty, and see what you can create.",
            "Bring your curiosity and leave with a new skill to show for it.",
            "All materials are provided, so all you need to bring is yourself.",
            "Give it a go and discover just how satisfying learning something new can be.",
        ],
    },

    "Not For the Faint of Heart": {
        "openings": [
            "Some evenings are better spent somewhere perfectly safe. This is not one of them.",
            "If ordinary nights out have stopped being interesting, perhaps it's time to try something a little darker.",
            "There are places you probably shouldn't visit after dark. Unfortunately, this event is taking you to one of them.",
            "Leave your sensible evening plans at home and prepare for something considerably less comfortable.",
            "Tonight's experience is designed for people who enjoy being unsettled, surprised, and just a little bit nervous.",
        ],
        "activities": [
            "Explore forgotten rooms, dark corridors, and places with stories that have never been properly explained.",
            "Follow the clues, investigate the surroundings, and discover what happened here after everyone else went home.",
            "You'll be guided through an immersive experience where the line between performance and reality starts becoming rather uncomfortable.",
            "Move through the location in a small group while strange sounds, unsettling discoveries, and unexpected moments unfold around you.",
            "Piece together the story as you explore, but don't expect every question to receive an answer.",
        ],
        "experiences": [
            "The experience is immersive, atmospheric, and deliberately unsettling, with plenty of moments designed to keep you guessing.",
            "Expect darkness, unexpected noises, and the occasional moment where you'll question whether you really saw something move.",
            "Nothing here is designed to leave you feeling completely comfortable, and that's rather the point.",
            "You may laugh, you may jump, and you may spend the journey home wondering whether that sound followed you.",
            "This isn't a gentle ghost story. It's an experience designed to get under your skin and stay there.",
        ],
        "closings": [
            "Bring your courage, stay close to the group, and try not to look behind you.",
            "The lights are going down soon. You have been warned.",
            "If you're brave enough to enter, we'll see you on the other side.",
            "Come if you dare. Leave if you can.",
        ],
    },
}


def generate_category_description(category):
    """Build a fresh, varied description for an event."""

    data = CATEGORY_DESCRIPTION_DATA[category]

    sentences = [
        random.choice(data["openings"]),
        random.choice(data["activities"]),
        random.choice(data["experiences"]),
    ]

    # Usually add a fourth sentence.
    if random.random() < 0.85:
        sentences.append(random.choice(data["experiences"]))

    # Roughly half the descriptions get a closing sentence.
    if random.random() < 0.55:
        sentences.append(random.choice(data["closings"]))

    # Remove accidental duplicate sentences.
    unique_sentences = []

    for sentence in sentences:
        if sentence not in unique_sentences:
            unique_sentences.append(sentence)

    return " ".join(unique_sentences)


# Map event titles to the more specific description themes where one exists.
# Events without a close theme match fall back to their broader category data.
DESCRIPTION_THEME_BY_TITLE = {
    # Adventure
    "Hidden History Walking Tour": "walking_tour",
    "After Dark City Tour": "walking_tour",
    "Riverside Kayaking Experience": "kayaking",
    "Sunset Woodland Walk": "hiking",
    "Canal Canoeing Challenge": "kayaking",
    "Sunrise Hilltop Hike": "hiking",
    "Urban Climbing Taster": "climbing",
    "Orienteering Challenge": "orienteering",
    "The Great City Treasure Hunt": "orienteering",

    # Arts & Culture
    "Beginner's Pottery Workshop": "pottery",
    "Introduction to Watercolour": "watercolour",
    "Local Artists Exhibition Night": "exhibition",
    "Museum After Hours": "exhibition",

    # Family
    "Family Science Day": "family_science",
    "Build Your Own Rocket": "family_science",
    "Dinosaur Discovery Day": "family_science",
    "Outdoor Treasure Hunt": "treasure_hunt",

    # Food & Drink
    "Evening Street Food Tour": "street_food",
    "Local Food & Market Walk": "street_food",
    "World Street Food Festival": "street_food",
    "Artisan Chocolate Workshop": "chocolate",
    "Dessert Decorating Workshop": "chocolate",
    "Pasta From Scratch": "pasta",

    # Music & Entertainment
    "Live Acoustic Night": "acoustic_music",
    "Indie Unplugged": "acoustic_music",
    "Battle of the Bands": "acoustic_music",
    "Open Mic Night": "acoustic_music",
    "Tribute Night Live": "acoustic_music",
    "Jazz Under the Stars": "jazz",
    "Vinyl DJ Night": "jazz",
    "Comedy Club Night": "comedy",
    "Comedy Improv Evening": "comedy",

    # Workshops
    "Beginner's Photography Walk": "photography",
    "Introduction to Wood Carving": "woodworking",
    "Furniture Restoration Basics": "woodworking",
    "Introduction to Screen Printing": "screen_printing",

    # Not For the Faint of Heart
    "The Last Showing": "horror_experience",
    "After Midnight": "horror_experience",
    "The Empty Room": "horror_experience",
    "The House at the End of the Lane": "horror_experience",
    "The Last Broadcast": "horror_experience",
    "Room 13": "horror_experience",
    "The Red Door": "horror_experience",
    "The Night Shift": "horror_experience",
    "Something in the Woods": "horror_experience",
    "Last Train Home": "horror_experience",
}


def generate_description(event_data):
    """Generate a varied description appropriate to the selected event."""

    theme = DESCRIPTION_THEME_BY_TITLE.get(event_data["name"])

    # Where we have a specific theme, mix both generators so repeated seed runs
    # do not make every event with the same title read identically.
    if theme and random.random() < 0.7:
        return generate_theme_description(theme)

    return generate_category_description(event_data["category"])


# EVENT CATALOGUE

EVENT_DATA = [

    # ADVENTURE

    {
        "category": "Adventure",
        "name": "Hidden History Walking Tour",
        "location": "Town Hall Steps",
        "time": time(14, 0),
        "price": Decimal("15.00"),
        "capacity": 25,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "After Dark City Tour",
        "location": "Old Town Gate",
        "time": time(19, 30),
        "price": Decimal("18.00"),
        "capacity": 20,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "Riverside Kayaking Experience",
        "location": "Riverside Boathouse",
        "time": time(10, 0),
        "price": Decimal("42.00"),
        "capacity": 12,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "Sunset Woodland Walk",
        "location": "Pinewood Trail Entrance",
        "time": time(18, 30),
        "price": Decimal("12.00"),
        "capacity": 20,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "Canal Canoeing Challenge",
        "location": "Canal Basin",
        "time": time(11, 0),
        "price": Decimal("35.00"),
        "capacity": 14,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "Sunrise Hilltop Hike",
        "location": "Hilltop Car Park",
        "time": time(5, 30),
        "price": Decimal("16.00"),
        "capacity": 18,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "Urban Climbing Taster",
        "location": "Summit Climbing Centre",
        "time": time(18, 0),
        "price": Decimal("28.00"),
        "capacity": 16,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "Orienteering Challenge",
        "location": "Ranger Station",
        "time": time(10, 30),
        "price": Decimal("14.00"),
        "capacity": 30,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "Outdoor Survival Skills",
        "location": "Pinewood Outdoor Centre",
        "time": time(9, 30),
        "price": Decimal("40.00"),
        "capacity": 15,
        "is_special": False,
    },
    {
        "category": "Adventure",
        "name": "The Great City Treasure Hunt",
        "location": "Market Square",
        "time": time(13, 0),
        "price": Decimal("17.00"),
        "capacity": 40,
        "is_special": False,
    },

    # ARTS & CULTURE

    {
        "category": "Arts & Culture",
        "name": "Beginner's Pottery Workshop",
        "location": "The Old Kiln Studio",
        "time": time(18, 30),
        "price": Decimal("32.00"),
        "capacity": 12,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Introduction to Watercolour",
        "location": "Riverside Arts Centre",
        "time": time(14, 0),
        "price": Decimal("24.00"),
        "capacity": 16,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Local Artists Exhibition Night",
        "location": "Eastside Gallery",
        "time": time(18, 0),
        "price": Decimal("8.00"),
        "capacity": 50,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Printmaking for Beginners",
        "location": "Riverside Arts Centre",
        "time": time(18, 30),
        "price": Decimal("27.00"),
        "capacity": 14,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Museum After Hours",
        "location": "City Museum",
        "time": time(19, 0),
        "price": Decimal("12.00"),
        "capacity": 35,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Life Drawing Evening",
        "location": "Studio Seven",
        "time": time(19, 30),
        "price": Decimal("22.00"),
        "capacity": 18,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Poetry & Performance Night",
        "location": "The Lantern Room",
        "time": time(19, 0),
        "price": Decimal("10.00"),
        "capacity": 60,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Independent Film Night",
        "location": "The Grand Cinema",
        "time": time(20, 0),
        "price": Decimal("13.00"),
        "capacity": 70,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Introduction to Calligraphy",
        "location": "The Makers' Room",
        "time": time(18, 0),
        "price": Decimal("21.00"),
        "capacity": 15,
        "is_special": False,
    },
    {
        "category": "Arts & Culture",
        "name": "Candlelit Storytelling Evening",
        "location": "Old Assembly Rooms",
        "time": time(19, 30),
        "price": Decimal("11.00"),
        "capacity": 45,
        "is_special": False,
    },

    # FAMILY

    {
        "category": "Family",
        "name": "Family Science Day",
        "location": "Discovery Centre",
        "time": time(11, 0),
        "price": Decimal("10.00"),
        "capacity": 40,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Outdoor Treasure Hunt",
        "location": "Central Park Pavilion",
        "time": time(12, 0),
        "price": Decimal("9.00"),
        "capacity": 30,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Junior Nature Explorers",
        "location": "Meadowlands Visitor Centre",
        "time": time(10, 30),
        "price": Decimal("11.00"),
        "capacity": 24,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Build Your Own Rocket",
        "location": "Discovery Centre",
        "time": time(13, 0),
        "price": Decimal("15.00"),
        "capacity": 25,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Dinosaur Discovery Day",
        "location": "Natural History Centre",
        "time": time(10, 0),
        "price": Decimal("13.00"),
        "capacity": 45,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Mini Makers Workshop",
        "location": "The Makers' Room",
        "time": time(11, 30),
        "price": Decimal("14.00"),
        "capacity": 18,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Family Board Game Café",
        "location": "The Dice Cup",
        "time": time(13, 30),
        "price": Decimal("8.00"),
        "capacity": 50,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Campfire Stories",
        "location": "Pinewood Outdoor Centre",
        "time": time(18, 0),
        "price": Decimal("12.00"),
        "capacity": 35,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Family Movie Afternoon",
        "location": "The Grand Cinema",
        "time": time(14, 0),
        "price": Decimal("12.00"),
        "capacity": 80,
        "is_special": False,
    },
    {
        "category": "Family",
        "name": "Junior Art Adventure",
        "location": "Riverside Arts Centre",
        "time": time(11, 0),
        "price": Decimal("10.00"),
        "capacity": 20,
        "is_special": False,
    },

    # FOOD & DRINK

    {
        "category": "Food & Drink",
        "name": "Evening Street Food Tour",
        "location": "Market Square",
        "time": time(18, 0),
        "price": Decimal("35.00"),
        "capacity": 18,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "Artisan Chocolate Workshop",
        "location": "Cocoa House",
        "time": time(18, 30),
        "price": Decimal("38.00"),
        "capacity": 12,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "Pasta From Scratch",
        "location": "The Green Kitchen",
        "time": time(18, 0),
        "price": Decimal("40.00"),
        "capacity": 14,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "Coffee Tasting Experience",
        "location": "Bean & Brew",
        "time": time(10, 30),
        "price": Decimal("24.00"),
        "capacity": 16,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "Bake Your Own Pizza",
        "location": "The Pizza Yard",
        "time": time(18, 30),
        "price": Decimal("28.00"),
        "capacity": 20,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "Local Food & Market Walk",
        "location": "Central Market",
        "time": time(11, 0),
        "price": Decimal("22.00"),
        "capacity": 20,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "Seasonal Supper Club",
        "location": "The Green Kitchen",
        "time": time(19, 30),
        "price": Decimal("45.00"),
        "capacity": 24,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "Dessert Decorating Workshop",
        "location": "Sugar & Spoon Studio",
        "time": time(14, 0),
        "price": Decimal("26.00"),
        "capacity": 14,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "World Street Food Festival",
        "location": "Festival Square",
        "time": time(12, 0),
        "price": Decimal("10.00"),
        "capacity": 150,
        "is_special": False,
    },
    {
        "category": "Food & Drink",
        "name": "The Great Afternoon Tea",
        "location": "The Grand Hotel",
        "time": time(15, 0),
        "price": Decimal("32.00"),
        "capacity": 40,
        "is_special": False,
    },

    # MUSIC & ENTERTAINMENT

    {
        "category": "Music & Entertainment",
        "name": "Live Acoustic Night",
        "location": "The Lantern Room",
        "time": time(20, 0),
        "price": Decimal("16.00"),
        "capacity": 80,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Indie Unplugged",
        "location": "The Backroom",
        "time": time(19, 30),
        "price": Decimal("14.00"),
        "capacity": 60,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Jazz Under the Stars",
        "location": "Riverside Gardens",
        "time": time(20, 30),
        "price": Decimal("20.00"),
        "capacity": 100,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Comedy Club Night",
        "location": "The Comedy Cellar",
        "time": time(20, 0),
        "price": Decimal("18.00"),
        "capacity": 70,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Vinyl DJ Night",
        "location": "The Record Room",
        "time": time(20, 0),
        "price": Decimal("15.00"),
        "capacity": 90,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Battle of the Bands",
        "location": "The Warehouse",
        "time": time(19, 0),
        "price": Decimal("17.00"),
        "capacity": 120,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Silent Disco",
        "location": "The Old Mill",
        "time": time(20, 30),
        "price": Decimal("19.00"),
        "capacity": 100,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Open Mic Night",
        "location": "The Lantern Room",
        "time": time(19, 0),
        "price": Decimal("8.00"),
        "capacity": 70,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Comedy Improv Evening",
        "location": "The Comedy Cellar",
        "time": time(19, 30),
        "price": Decimal("16.00"),
        "capacity": 65,
        "is_special": False,
    },
    {
        "category": "Music & Entertainment",
        "name": "Tribute Night Live",
        "location": "The Grand Hall",
        "time": time(20, 0),
        "price": Decimal("25.00"),
        "capacity": 150,
        "is_special": False,
    },

    # WORKSHOPS

    {
        "category": "Workshops",
        "name": "Leathercraft for Beginners",
        "location": "Forge & Foundry Workshop",
        "time": time(18, 0),
        "price": Decimal("36.00"),
        "capacity": 10,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Introduction to Wood Carving",
        "location": "The Workshop Loft",
        "time": time(13, 30),
        "price": Decimal("30.00"),
        "capacity": 10,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Beginner's Photography Walk",
        "location": "Riverside Bridge",
        "time": time(10, 0),
        "price": Decimal("20.00"),
        "capacity": 15,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Creative Writing Evening",
        "location": "The Writers' Room",
        "time": time(19, 0),
        "price": Decimal("18.00"),
        "capacity": 16,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Introduction to 3D Printing",
        "location": "Digital Makers Lab",
        "time": time(18, 0),
        "price": Decimal("29.00"),
        "capacity": 12,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Build Your Own Terrarium",
        "location": "Greenhouse Studio",
        "time": time(18, 30),
        "price": Decimal("25.00"),
        "capacity": 14,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Digital Illustration Basics",
        "location": "Digital Makers Lab",
        "time": time(18, 30),
        "price": Decimal("27.00"),
        "capacity": 15,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Furniture Restoration Basics",
        "location": "The Workshop Loft",
        "time": time(10, 0),
        "price": Decimal("35.00"),
        "capacity": 10,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Natural Soap Making",
        "location": "The Makers' Room",
        "time": time(18, 0),
        "price": Decimal("28.00"),
        "capacity": 12,
        "is_special": False,
    },
    {
        "category": "Workshops",
        "name": "Introduction to Screen Printing",
        "location": "Print House Studio",
        "time": time(18, 30),
        "price": Decimal("31.00"),
        "capacity": 12,
        "is_special": False,
    },

    # NOT FOR THE FAINT OF HEART

    {
        "category": "Not For the Faint of Heart",
        "name": "The Last Showing",
        "location": "The Old Picture House",
        "time": time(23, 0),
        "price": Decimal("25.00"),
        "capacity": 24,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "After Midnight",
        "location": "Old District",
        "time": time(23, 30),
        "price": Decimal("22.00"),
        "capacity": 16,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "The Empty Room",
        "location": "The Old Assembly Rooms",
        "time": time(21, 30),
        "price": Decimal("28.00"),
        "capacity": 12,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "The House at the End of the Lane",
        "location": "Blackthorn Lane",
        "time": time(22, 0),
        "price": Decimal("30.00"),
        "capacity": 10,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "The Last Broadcast",
        "location": "Station Nine",
        "time": time(23, 0),
        "price": Decimal("27.00"),
        "capacity": 14,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "Room 13",
        "location": "The Grand Hotel",
        "time": time(22, 30),
        "price": Decimal("26.00"),
        "capacity": 12,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "The Red Door",
        "location": "Blackwood House",
        "time": time(21, 0),
        "price": Decimal("29.00"),
        "capacity": 10,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "The Night Shift",
        "location": "Westgate Offices",
        "time": time(22, 0),
        "price": Decimal("24.00"),
        "capacity": 18,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "Something in the Woods",
        "location": "Pinewood Forest",
        "time": time(22, 30),
        "price": Decimal("23.00"),
        "capacity": 15,
        "is_special": True,
    },
    {
        "category": "Not For the Faint of Heart",
        "name": "Last Train Home",
        "location": "Old Central Station",
        "time": time(23, 45),
        "price": Decimal("32.00"),
        "capacity": 20,
        "is_special": True,
    },
]


def select_event_templates(count):
    """Randomly choose event templates without repeating titles unnecessarily."""

    category_events = {}

    for event_data in EVENT_DATA:
        category_events.setdefault(
            event_data["category"], []
        ).append(event_data)

    category_names = list(category_events.keys())
    selected_events = []

    if count <= len(EVENT_DATA):
        # If enough events are requested, guarantee at least one per category.
        if count >= len(category_names):
            for category_name in category_names:
                selected_events.append(
                    random.choice(category_events[category_name])
                )

            selected_names = {event["name"] for event in selected_events}
            remaining_events = [
                event for event in EVENT_DATA
                if event["name"] not in selected_names
            ]
            random.shuffle(remaining_events)
            selected_events.extend(
                remaining_events[:count - len(selected_events)]
            )
        else:
            selected_events = random.sample(EVENT_DATA, count)
    else:
        # Exhaust the full catalogue before allowing titles to repeat.
        remaining = count

        while remaining > 0:
            batch = EVENT_DATA.copy()
            random.shuffle(batch)

            # Prevent the first item in a recycled batch from repeating the
            # title immediately before it, even if only one item is needed.
            if (
                selected_events
                and batch[0]["name"] == selected_events[-1]["name"]
            ):
                for swap_index in range(1, len(batch)):
                    if (
                        batch[swap_index]["name"]
                        != selected_events[-1]["name"]
                    ):
                        batch[0], batch[swap_index] = (
                            batch[swap_index],
                            batch[0],
                        )
                        break

            take = min(remaining, len(batch))
            selected_events.extend(batch[:take])
            remaining -= take

    return selected_events


# MANAGEMENT COMMAND

class Command(BaseCommand):
    help = "Create a collection of sample events for Event Horizon."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=len(EVENT_DATA),
            help="Number of events to create.",
        )

        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing events before creating new ones.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        clear = options["clear"]

        if count < 1:
            self.stdout.write(
                self.style.ERROR("Count must be at least 1.")
            )
            return

        if clear:
            deleted, _ = Event.objects.all().delete()

            self.stdout.write(
                self.style.WARNING(
                    f"Deleted {deleted} existing event record(s)."
                )
            )

        # Create categories automatically if they do not already exist.
        categories = {}

        for event_data in EVENT_DATA:
            category_name = event_data["category"]

            if category_name not in categories:
                category, _ = Category.objects.get_or_create(
                    name=category_name
                )
                categories[category_name] = category

        selected_events = select_event_templates(count)

        # Create the events.

        start_date = timezone.localdate() + timedelta(days=7)

        created = 0

        for event_data in selected_events:

            event_date = start_date + timedelta(
                days=random.randint(0, 60)
            )

            description = generate_description(event_data)

            event = Event.objects.create(
                category=categories[event_data["category"]],
                name=event_data["name"],
                description=description,
                location=event_data["location"],
                date=event_date,
                time=event_data["time"],
                price=event_data["price"],
                capacity=event_data["capacity"],
                active=True,
                is_special=event_data["is_special"],
            )

            created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created: {event.name} "
                    f"({event.date})"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully created {created} event(s)."
            )
        )
