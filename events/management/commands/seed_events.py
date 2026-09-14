from datetime import time, timedelta
from decimal import Decimal
from pathlib import Path
import random

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from events.models import Category, Event

# DESCRIPTION GENERATORS

# BASE CODE BY MYSELF, FULLY IMPLEMENTED BY CHATGPT

THEME_DESCRIPTION_DATA = {

    "hidden_history": {
        "category": "Adventure",
        "openings": [
            "Take a leisurely walk through the town while uncovering some of the stories hiding in plain sight.",
            "Take a closer look at streets you may have walked dozens of times on a tour built around the town's overlooked history.",
            "Step beyond the obvious landmarks and discover the people, places, and events woven into the town's past.",
        ],
        "activities": [
            "Follow an experienced local guide through historic streets, forgotten corners, and landmarks that are easy to overlook.",
            "Trace a route through the town while hearing stories about unusual characters, dramatic events, and buildings with more history than their modern surroundings suggest.",
            "Stop at carefully chosen locations where your guide will reveal details and stories that are easy to miss when simply walking past.",
        ],
        "details": [
            "Whether you're new to the area or have lived here for years, there is always another story waiting to be uncovered.",
            "The relaxed pace leaves plenty of time to look around, ask questions, and notice details you may never have spotted before.",
            "By the end of the route, everyday surroundings may carry a surprising amount of history you never knew was there.",
        ],
        "closings": [
            "Bring comfortable shoes, a little curiosity, and let the town tell its story.",
            "Come curious and leave with a few local stories worth retelling.",
        ],
    },

    "after_dark_city": {
        "category": "Adventure",
        "openings": [
            "Watch the city change character once daylight disappears and the streets begin to quieten.",
            "Explore the city after dark, when busy streets quieten down and old corners take on a completely different atmosphere.",
            "Wait until evening, then follow the city into the stories that only seem to belong after sunset.",
        ],
        "activities": [
            "Follow your guide through atmospheric lanes, old squares, and quieter corners while hearing stories connected to the city's night-time history.",
            "Walk a carefully planned evening route through historic streets while discovering local legends, unusual events, and places with stories best told after dark.",
            "Explore landmarks and hidden corners that take on a different character at night while your guide brings their stranger histories to life.",
        ],
        "details": [
            "Expect local legends, dramatic events, and places that take on an entirely different character once most people have gone home.",
            "The experience is atmospheric rather than frightening, combining history, storytelling, and the particular mood of the city at night.",
            "Even places you know well can feel unfamiliar when the crowds thin out and the streetlights take over.",
        ],
        "closings": [
            "Bring comfortable shoes, stay with the group, and discover the city after dark.",
            "Wrap up warm, keep your eyes open, and see what the city reveals after sunset.",
        ],
    },

    "riverside_kayaking": {
        "category": "Adventure",
        "openings": [
            "Get out on the water for an active few hours of paddling, fresh air, and riverside exploration.",
            "Swap the riverbank for a kayak and discover the local landscape from water level.",
            "Grab a paddle and spend a few hours building confidence while exploring the river from a completely different perspective.",
        ],
        "activities": [
            "Learn the basics of kayaking before heading along the river with guidance from an experienced instructor.",
            "Practise paddling, steering, and basic safety before setting out together on a beginner-friendly riverside route.",
            "An instructor will help you get comfortable in the kayak before the group heads out to explore a gentle stretch of river.",
        ],
        "details": [
            "No previous kayaking experience is required, and there will be plenty of time to build confidence on the water.",
            "The session balances practical instruction with enough time to relax, enjoy the scenery, and get used to moving across the water.",
            "Expect useful techniques, plenty of encouragement, and the occasional splash while you learn at a comfortable pace.",
        ],
        "closings": [
            "Bring suitable outdoor clothing and get ready to make a splash.",
            "Grab your paddle, leave the riverbank behind, and enjoy the journey.",
        ],
    },

    "sunset_woodland": {
        "category": "Adventure",
        "openings": [
            "Spend the evening following peaceful woodland trails as the light begins to fade through the trees.",
            "Head into the woods for a gentle walk timed to catch the landscape shifting around sunset.",
            "Slow the pace down with a guided woodland walk through the final light of the day.",
        ],
        "activities": [
            "Follow quiet forest paths, open clearings, and scenic viewpoints selected to make the most of the evening light.",
            "Walk a relaxed route through the woodland while your guide points out natural features, viewpoints, and signs of evening wildlife.",
            "The route winds through wooded trails and open viewpoints, giving the group plenty of chances to stop and enjoy the changing light.",
        ],
        "details": [
            "The pace is relaxed, leaving time to enjoy the surroundings, take photographs, and notice the woodland settling towards dusk.",
            "It is a peaceful way to experience the woods at a time of day when the atmosphere, colours, and sounds begin to shift.",
            "No specialist walking experience is needed, just comfortable footwear and a willingness to take the evening slowly.",
        ],
        "closings": [
            "Bring comfortable footwear and enjoy the woods at one of their most atmospheric times of day.",
            "Take your time, watch the last light fade, and let the woods grow quiet around you.",
        ],
    },

    "canal_canoeing": {
        "category": "Adventure",
        "openings": [
            "Take to the canal for a paddling challenge that mixes technique, teamwork, and a little friendly competition.",
            "Climb into a canoe and find out how well two paddlers can work together when the course starts asking questions.",
            "Turn a calm stretch of canal into a hands-on canoeing challenge built around coordination and control.",
        ],
        "activities": [
            "After learning the basics of handling a canoe, you'll navigate a planned route featuring turns, checkpoints, and practical challenges along the way.",
            "Work with your paddling partner to steer through a marked course while tackling navigation tasks and skill-based checkpoints.",
            "An instructor will cover the essentials before teams take on a canal course designed to test steering, communication, and paddle control.",
        ],
        "details": [
            "The challenge is beginner-friendly, but smooth teamwork can make a very noticeable difference once the canoe starts drifting off line.",
            "Expect a few splashes, plenty of encouragement, and a much better understanding of why two people agreeing which way to paddle matters.",
            "It is less about outright speed and more about working together, reading the course, and keeping the canoe heading where you intended.",
        ],
        "closings": [
            "Bring suitable outdoor clothing and your best teamwork.",
            "Pick a paddling partner, trust each other, and try to keep the canoe pointing forwards.",
        ],
    },

    "sunrise_hilltop": {
        "category": "Adventure",
        "openings": [
            "Start the day before most people are awake and make your way towards high ground in time for sunrise.",
            "Set out in the quiet of early morning for a guided hike with sunrise waiting at the top.",
            "Trade the snooze button for walking boots and watch the landscape wake up from a hilltop viewpoint.",
        ],
        "activities": [
            "Follow a guided trail through the early-morning landscape as the light gradually changes around you.",
            "Your guide will lead a steady route towards the summit, allowing time for short stops and changing views along the climb.",
            "Walk through the pre-dawn landscape before reaching a hilltop spot chosen for a wide view of the rising sun.",
        ],
        "details": [
            "The climb is steady rather than competitive, with time built in to catch your breath and enjoy the views along the way.",
            "Arriving before the sun appears gives the group time to settle in and watch the colours spread across the landscape.",
            "An early start is required, but the reward is seeing the day arrive from somewhere considerably better than the kitchen window.",
        ],
        "closings": [
            "Bring warm layers, sensible footwear, and something worth waking up early for.",
            "Reach the summit, settle in, and watch the new day arrive.",
        ],
    },

    "urban_climbing": {
        "category": "Adventure",
        "openings": [
            "Challenge yourself to try something new with an introduction to indoor climbing.",
            "Put balance, movement, and problem-solving to work on an indoor climbing session designed for beginners.",
            "Ready to get off the ground? This beginner-friendly climbing taster gives you the chance to learn the basics safely.",
        ],
        "activities": [
            "Experienced instructors will introduce you to essential safety, movement, balance, and route-reading before helping you tackle beginner-friendly walls.",
            "Learn how to approach the wall, use your feet effectively, and read climbing routes before putting the techniques into practice.",
            "After a safety briefing and introduction to basic movement, you'll work through a selection of routes with support from an instructor.",
        ],
        "details": [
            "Each route presents a slightly different puzzle, so success is as much about thinking as it is about strength.",
            "No previous experience is required, and you can climb at a level that suits your confidence.",
            "The focus is on learning good fundamentals, trying different routes, and enjoying the satisfaction of solving your way to the top.",
        ],
        "closings": [
            "Trust your feet, take your time, and see how high you can get.",
            "Start at your own level and discover why reaching the top is so satisfying.",
        ],
    },

    "orienteering_challenge": {
        "category": "Adventure",
        "openings": [
            "Put your navigation skills to the test with a course built around maps, checkpoints, and quick decisions.",
            "Grab a map, find your bearings, and take on an outdoor challenge where choosing the route is part of the game.",
            "See how well your sense of direction survives a course designed around navigation rather than signposts.",
        ],
        "activities": [
            "After a short introduction to map reading and route planning, you'll set out to locate a series of markers spread across the surrounding area.",
            "Use a map and the landscape around you to navigate between checkpoints while deciding which route gives you the best chance of a clean run.",
            "Teams or individual participants will work through a sequence of checkpoints using observation, map reading, and careful route choices.",
        ],
        "details": [
            "Choosing the shortest path is not always the easiest option, so careful navigation can matter just as much as speed.",
            "The challenge rewards observation and decision-making, and getting slightly lost is acceptable provided you eventually correct course.",
            "Beginners are welcome, with enough guidance at the start to make the course approachable without removing the challenge.",
        ],
        "closings": [
            "Keep your bearings, trust the map, and see how efficiently you can find them all.",
            "Plan the route, watch the map, and try not to discover the same checkpoint twice.",
        ],
    },

    "outdoor_survival": {
        "category": "Adventure",
        "openings": [
            "Spend the day learning practical outdoor skills designed to make the wilderness feel a little less mysterious.",
            "Step into the outdoors for a practical introduction to the skills that help people stay comfortable and capable away from everyday conveniences.",
            "Learn how to approach the outdoors with more confidence in a hands-on survival skills session for beginners.",
        ],
        "activities": [
            "Practise techniques such as shelter building, fire preparation, basic navigation, and identifying useful resources in the landscape.",
            "An experienced instructor will demonstrate core outdoor skills before giving you the chance to practise them for yourself.",
            "Work through a series of practical tasks covering shelter, navigation, safe fire preparation, and making sensible use of the surroundings.",
        ],
        "details": [
            "No previous experience is required, just sensible outdoor clothing and a willingness to learn by doing.",
            "The emphasis is on practical, responsible techniques rather than dramatic survival scenarios, with guidance available throughout.",
            "By the end of the session, you should have a better understanding of how planning, observation, and simple skills can make a big difference outdoors.",
        ],
        "closings": [
            "Bring sensible outdoor clothing and prepare to learn by doing.",
            "Leave the gadgets behind for a few hours and discover how useful a few practical skills can be.",
        ],
    },

    "city_treasure_hunt": {
        "category": "Adventure",
        "openings": [
            "Turn the city into a giant puzzle as your team races to solve clues and uncover the next location.",
            "Gather your team and prepare to see the city as a trail of riddles, hidden details, and unexpected discoveries.",
            "Think you know the city? This treasure hunt is designed to make you look at familiar streets much more carefully.",
        ],
        "activities": [
            "Follow riddles, photographs, hidden details, and cryptic hints through streets and landmarks you may have walked past dozens of times before.",
            "Each solved clue points towards another location, sending teams across the city in search of details hiding in plain sight.",
            "Work together to crack a sequence of puzzles that use landmarks, signs, architecture, and observation to reveal the route.",
        ],
        "details": [
            "Each solved challenge reveals another piece of the trail until your team reaches the final destination.",
            "Observation, teamwork, and creative thinking will get you much further than simply running in whichever direction looks promising.",
            "The hunt is designed to reward sharp eyes and good teamwork, with enough twists to keep even familiar streets interesting.",
        ],
        "closings": [
            "Gather your team, sharpen your detective skills, and see if you can reach the final clue.",
            "Keep your eyes open, trust your teammates, and let the city become the puzzle.",
        ],
    },

    "beginner_pottery": {
        "category": "Arts & Culture",
        "openings": [
            "Get your hands into clay and discover how satisfying it is to turn a simple lump of material into something entirely your own.",
            "Spend a relaxed evening learning how a piece of clay can become something useful, decorative, or wonderfully unexpected.",
            "Roll up your sleeves and try pottery in a beginner-friendly session built around learning by doing.",
        ],
        "activities": [
            "An experienced potter will introduce basic shaping, moulding, and decorating techniques before giving you time to create your own piece.",
            "Learn how to prepare and shape clay before experimenting with simple forms, textures, and decorative details.",
            "Work through the foundations of hand-building and decoration, then use those techniques to make a piece of your own.",
        ],
        "details": [
            "The workshop is designed for complete beginners, so wonky edges and unexpected shapes are very much part of the process.",
            "There is no pressure to create a masterpiece, and plenty of room to experiment while you get used to working with the material.",
            "You will have guidance throughout while still having enough freedom to follow your own ideas and see where the clay takes you.",
        ],
        "closings": [
            "Roll up your sleeves, embrace the mess, and see what your hands can create.",
            "Come ready to experiment, get a little messy, and make something that is completely yours.",
        ],
    },

    "intro_watercolour": {
        "category": "Arts & Culture",
        "openings": [
            "Pick up a brush and discover how water, pigment, and a little patience can transform a blank page.",
            "Spend a peaceful creative session exploring the soft colours and expressive possibilities of watercolour painting.",
            "Slow things down and learn the foundations of watercolour in a relaxed setting designed for complete beginners.",
        ],
        "activities": [
            "Explore washes, colour mixing, layering, and brush control before bringing the techniques together in a finished painting.",
            "Work through practical exercises covering colour, water control, and simple brush techniques before creating a piece of your own.",
            "Experiment with transparent layers, blended colours, and different amounts of water while learning how watercolour behaves on the page.",
        ],
        "details": [
            "The focus is on experimentation rather than perfection, so unexpected blooms and wandering colour are all part of learning the medium.",
            "Beginners are encouraged to test different approaches and discover how small changes in water and pigment can completely alter the result.",
            "There will be plenty of guidance, but also enough freedom to develop your own style as your confidence grows.",
        ],
        "closings": [
            "Bring your curiosity and let the colours do some of the decision-making.",
            "Expect a relaxed session, a colourful page, and at least one happy accident worth keeping.",
        ],
    },

    "local_artists_exhibition": {
        "category": "Arts & Culture",
        "openings": [
            "Spend an evening discovering work created by artists from across the local area.",
            "Step into the gallery for a celebration of local creativity featuring emerging and established artists.",
            "Explore an exhibition that brings together a broad mix of work from artists working close to home.",
        ],
        "activities": [
            "Browse paintings, photography, sculpture, and mixed-media pieces while meeting some of the people behind the work.",
            "Take your time exploring the collection and hear artists talk about the ideas, techniques, and experiences that shaped selected pieces.",
            "Move through a varied collection of local work while chatting with artists and fellow visitors about what catches your attention.",
        ],
        "details": [
            "The exhibition mixes different styles and perspectives, so there is plenty to discover even if you arrive without knowing exactly what you like.",
            "The relaxed atmosphere makes it easy to browse at your own pace, ask questions, and spend longer with the pieces that hold your attention.",
            "A broad mix of styles and perspectives gives the evening a lively snapshot of the local creative scene.",
        ],
        "closings": [
            "Take your time, ask questions, and see which piece refuses to leave your head afterwards.",
            "Come curious and leave with a few new artists to remember.",
        ],
    },

    "printmaking_beginners": {
        "category": "Arts & Culture",
        "openings": [
            "Discover the satisfying process of turning a simple design into a finished print.",
            "Get a little inky while learning how images can be built, transferred, and repeated through printmaking.",
            "Spend a hands-on creative session learning the basics of printmaking from first idea to final impression.",
        ],
        "activities": [
            "Learn how a design is prepared, inked, and pressed before creating a small set of prints of your own.",
            "Work through a beginner-friendly printmaking process while experimenting with shapes, texture, pressure, and colour.",
            "Create a simple design, prepare it for printing, apply ink, and experience the satisfying reveal when the finished print is lifted away.",
        ],
        "details": [
            "No previous experience is needed, and the emphasis is on understanding the process rather than producing identical perfect copies.",
            "Small differences between impressions are part of the character of printmaking, so experimentation is very much encouraged.",
            "You will have plenty of guidance while still having room to make creative choices and develop your own design.",
        ],
        "closings": [
            "Come ready to experiment, get a little inky, and leave with prints you made yourself.",
            "Bring an idea and an open mind, then let the press handle the dramatic reveal.",
        ],
    },

    "museum_after_hours": {
        "category": "Arts & Culture",
        "openings": [
            "Experience the museum after the daytime crowds have gone and the galleries have taken on a quieter atmosphere.",
            "Step into the museum after hours and discover how different the collections feel once the usual daytime bustle disappears.",
            "Spend an evening wandering the museum when the doors stay open beyond their normal closing time.",
        ],
        "activities": [
            "Explore selected galleries at your own pace while guides share stories, unusual objects, and details that are easy to overlook during a normal visit.",
            "Follow a relaxed route through the collections with opportunities to hear short talks and take a closer look at some of the museum's most intriguing pieces.",
            "Wander through the galleries and discover objects, displays, and stories highlighted especially for the evening programme.",
        ],
        "details": [
            "The quieter setting gives you more room to linger over the things that catch your attention instead of moving with the daytime crowd.",
            "Special interpretation and evening highlights add context to familiar displays and offer a few reasons to look twice at objects you might otherwise pass by.",
            "It is a chance to experience the collection at a slower pace and enjoy the atmosphere of the building after its usual working day is over.",
        ],
        "closings": [
            "Wander, linger, and enjoy having a little more room to let the past speak for itself.",
            "Stay curious, follow whatever catches your attention, and enjoy the museum in a different light.",
        ],
    },

    "life_drawing": {
        "category": "Arts & Culture",
        "openings": [
            "Spend an evening developing your observational drawing skills with a live model in a relaxed studio setting.",
            "Sharpen your eye as well as your pencil in a life drawing session designed to build confidence through observation.",
            "Settle into the studio for an evening focused on drawing the human figure from life.",
        ],
        "activities": [
            "Work through a mixture of short gesture poses and longer studies designed to explore proportion, movement, shape, and line.",
            "Begin with quick poses to loosen up before moving into longer studies where you can concentrate on structure, balance, and detail.",
            "Use a series of timed poses to practise observation, proportion, gesture, and the challenge of translating a three-dimensional figure onto the page.",
        ],
        "details": [
            "Guidance is available throughout, but the emphasis is on observing carefully and developing your own approach rather than producing a perfect drawing.",
            "Beginners are welcome, and the changing pose lengths give everyone opportunities to experiment without getting too precious about a single page.",
            "The session is supportive and informal, making it suitable both for first-time life drawing and for artists wanting regular practice.",
        ],
        "closings": [
            "Bring a willingness to look properly before putting pencil to paper.",
            "Take your time, trust your eye, and let each pose teach you something different.",
        ],
    },

    "poetry_performance": {
        "category": "Arts & Culture",
        "openings": [
            "Settle in for an evening of spoken word, poetry, storytelling, and live performance from a varied line-up of local voices.",
            "Spend the evening listening to words take centre stage as poets and performers share work in an intimate live setting.",
            "Join a room full of listeners for a night built around poetry, performance, and the particular energy of hearing new work spoken aloud.",
        ],
        "activities": [
            "Hear everything from quiet personal pieces to energetic spoken-word performances, humour, observation, and original storytelling.",
            "A changing line-up of writers and performers will take the microphone with original work covering a broad range of styles and subjects.",
            "Listen to established and emerging voices perform original pieces, with each performer bringing a different rhythm, tone, and perspective to the room.",
        ],
        "details": [
            "The informal setting keeps the audience close to the performers and gives new and experienced writers the same stage.",
            "Some pieces may make the room laugh while others leave it unexpectedly silent for a moment, and that contrast is part of the appeal.",
            "You do not need to know anything about poetry beforehand; the evening is built around listening, discovering new voices, and enjoying the performance itself.",
        ],
        "closings": [
            "Come to listen, discover someone new, and perhaps leave with a few lines still rattling around in your head.",
            "Find a seat, listen closely, and see which words stay with you after the microphone goes quiet.",
        ],
    },

    "independent_film": {
        "category": "Arts & Culture",
        "openings": [
            "Spend the evening discovering independent cinema beyond the usual blockbuster schedule.",
            "Take a seat for a film night dedicated to distinctive storytelling and voices from outside the mainstream.",
            "Swap the multiplex formula for an evening of independent cinema chosen to offer something a little less predictable.",
        ],
        "activities": [
            "A specially selected film will take centre stage, followed by an opportunity to discuss its themes, characters, production, and ideas with other film lovers.",
            "Watch a carefully chosen independent feature before staying for an informal conversation about the choices, themes, and ideas behind it.",
            "Settle in for a screening selected for its distinctive perspective, then join an optional discussion once the credits have finished.",
        ],
        "details": [
            "Expect unusual perspectives, creative risks, and the kind of filmmaking decisions that tend to spark conversation afterwards.",
            "The focus is on films that offer something different, whether through their subject, style, production, or the voices behind the camera.",
            "You do not need to be a film expert; curiosity and a willingness to try something unfamiliar are more than enough.",
        ],
        "closings": [
            "Find your seat, silence your phone, and give something outside the mainstream a chance to surprise you.",
            "Stay for the credits, stay for the conversation, and see where the film takes the room afterwards.",
        ],
    },

    "intro_calligraphy": {
        "category": "Arts & Culture",
        "openings": [
            "Slow things down and discover the careful art of creating beautiful letterforms by hand.",
            "Spend a relaxed session learning how deliberate strokes can turn everyday handwriting into something far more decorative.",
            "Pick up a calligraphy pen and discover how tiny adjustments can transform the appearance and character of a line of text.",
        ],
        "activities": [
            "Learn how pen angle, pressure, spacing, and stroke direction work together before practising basic shapes, alphabets, and simple words.",
            "Begin with foundational strokes and letter shapes before combining them into words and short phrases of your own.",
            "Practise controlled marks, consistent spacing, and simple letterforms while learning how the pen responds to pressure and movement.",
        ],
        "details": [
            "The session is designed for complete beginners, with plenty of time to repeat techniques and develop a steadier hand.",
            "Calligraphy rewards patience more than speed, so the workshop keeps the pace comfortable and gives you room to practise each movement properly.",
            "You will leave with a better understanding of the building blocks behind decorative lettering and exercises you can continue at home.",
        ],
        "closings": [
            "By the end, even writing your own name may feel considerably more ceremonial than it did when you arrived.",
            "Take your time, enjoy the rhythm of the strokes, and give ordinary words a little more occasion.",
        ],
    },

    "candlelit_storytelling": {
        "category": "Arts & Culture",
        "openings": [
            "Settle into the glow of candlelight for an evening devoted to stories told the old-fashioned way, one voice and one room at a time.",
            "Leave the screens behind and gather by candlelight for an intimate evening of stories, folklore, and imagination.",
            "As the room darkens and the candles take over, settle in for an evening where the only special effect required is a good storyteller.",
        ],
        "activities": [
            "A selection of storytellers will share folklore, unusual histories, traditional tales, and original pieces chosen to suit the intimate setting.",
            "Listen as performers bring legends, strange histories, and original stories to life using nothing more complicated than voice, timing, and imagination.",
            "The evening moves through a collection of spoken tales, from familiar folklore to original stories written for a room best enjoyed in low light.",
        ],
        "details": [
            "With no screen competing for attention, the atmosphere depends entirely on the words, the audience, and whatever your imagination adds in the darker corners of the room.",
            "The close setting makes every pause and change of tone feel more immediate, turning simple storytelling into something surprisingly atmospheric.",
            "Expect a mixture of warmth, humour, mystery, and the occasional tale that feels slightly more convincing once the room has gone quiet.",
        ],
        "closings": [
            "Get comfortable, listen closely, and let somebody else build the world for a while.",
            "Settle in, watch the candlelight, and see where the next story decides to take you.",
        ],
    },

    "family_science": {
        "category": "Family",
        "openings": [
            "Bring the whole family along for a day packed with experiments, demonstrations, and hands-on discoveries.",
            "Get ready for a family science day where curiosity is encouraged and almost everything is better when you can try it yourself.",
            "Turn questions into experiments with a family day devoted to discovering how the world works.",
        ],
        "activities": [
            "Children can investigate scientific ideas through practical activities designed to make learning feel more like exploration than a lesson.",
            "Move between interactive experiments, demonstrations, and challenges that invite young scientists to test ideas for themselves.",
            "Try a mixture of hands-on activities covering surprising scientific ideas, with plenty of chances to predict, test, and investigate.",
        ],
        "details": [
            "Expect plenty of questions, surprising results, and the occasional experiment that makes everyone in the room lean a little closer.",
            "The emphasis is on learning through doing, so children can get involved rather than simply watch from the sidelines.",
            "Grown-ups are encouraged to join in too, because curiosity does not come with an age limit.",
        ],
        "closings": [
            "Bring your curiosity and prepare to ask 'why does it do that?' more than once.",
            "Come ready to experiment, investigate, and discover something unexpected.",
        ],
    },

    "family_treasure_hunt": {
        "category": "Family",
        "openings": [
            "Gather the family and head outdoors for a clue-filled adventure through the local area.",
            "Put the family's detective skills to work on an outdoor treasure hunt built around riddles, clues, and hidden checkpoints.",
            "Grab your team and prepare for an outdoor trail where every solved clue points towards the next discovery.",
        ],
        "activities": [
            "Work together to solve riddles, follow the trail, and uncover hidden checkpoints scattered along the route.",
            "Follow a sequence of clues through the area, combining observation, teamwork, and a little creative thinking to stay on track.",
            "Search for hidden details, crack family-friendly puzzles, and use each answer to reveal the next part of the route.",
        ],
        "details": [
            "Everyone can contribute, whether they are good at spotting details, cracking puzzles, or confidently insisting the answer is definitely this way.",
            "The hunt is designed for different ages to work together, so sharp eyes can be just as useful as quick thinking.",
            "Expect teamwork, a few debates over directions, and the satisfaction of watching the final clue fall into place.",
        ],
        "closings": [
            "Bring your best detective skills and see if your team can reach the final clue.",
            "Gather your crew, keep your eyes open, and let the hunt begin.",
        ],
    },

    "junior_nature_explorers": {
        "category": "Family",
        "openings": [
            "Turn young explorers loose on the natural world with a session built around discovering what is living, growing, crawling, and hiding nearby.",
            "Head outdoors and give curious young minds the chance to investigate the plants, creatures, and clues hiding in the landscape.",
            "Put on your exploring shoes and discover how much wildlife can be hiding in places that first look completely ordinary.",
        ],
        "activities": [
            "Children will investigate plants, insects, tracks, habitats, and other signs of wildlife through hands-on outdoor activities.",
            "Search for natural clues, examine small discoveries, and learn how to recognise some of the signs animals and plants leave behind.",
            "Explore the surroundings with simple nature activities designed to encourage careful observation and plenty of questions.",
        ],
        "details": [
            "The emphasis is on noticing small details and asking questions about the environment around them.",
            "Activities are designed to make children look more closely at the world around them and think about how living things share the same spaces.",
            "No specialist knowledge is needed, just curiosity, suitable outdoor clothing, and a willingness to investigate.",
        ],
        "closings": [
            "Bring suitable outdoor clothing and prepare to discover what has been hiding nearby all along.",
            "Keep your eyes open, look closely, and see how much nature you can find.",
        ],
    },

    "build_your_own_rocket": {
        "category": "Family",
        "openings": [
            "Design, build, and launch a simple rocket while discovering some of the science that makes it leave the ground.",
            "Give young engineers a mission: build a rocket, understand what makes it fly, and then see whether the design survives launch day.",
            "Get ready for a hands-on family session where cardboard, creativity, and a little science all point in one direction: upwards.",
        ],
        "activities": [
            "Young engineers will experiment with shape, balance, and basic forces before putting their creation to the test in a supervised launch.",
            "Build a simple rocket step by step, make design choices, and then take it outside for a supervised countdown and launch.",
            "Explore the basic forces behind flight while constructing a rocket designed to turn theory into something much more exciting than a diagram.",
        ],
        "details": [
            "The session combines making, problem-solving, and just enough science to explain why some rockets fly beautifully while others develop more adventurous ideas about direction.",
            "The builders stay in charge throughout, with grown-ups nearby if an extra pair of hands is useful.",
            "Different designs may behave very differently at launch, which is exactly what makes testing them part of the fun.",
        ],
        "closings": [
            "When everything is ready, ownership of the final countdown belongs to the builders.",
            "Build it carefully, count it down loudly, and see where the launch takes it.",
        ],
    },

    "dinosaur_discovery": {
        "category": "Family",
        "openings": [
            "Step back into the prehistoric world for a family day filled with fossils, dinosaurs, and hands-on discovery.",
            "Invite young palaeontologists to investigate a world of fossils, ancient creatures, and clues preserved from millions of years ago.",
            "Travel back long before people arrived and spend the day uncovering what fossils can tell us about dinosaurs and their world.",
        ],
        "activities": [
            "Young palaeontologists can examine replica fossils, learn how scientists piece together evidence from the past, and explore what we know about the creatures that once walked the Earth.",
            "Handle replica specimens, investigate fossil clues, and discover how palaeontologists use evidence to reconstruct animals nobody has ever seen alive.",
            "Explore prehistoric life through family-friendly activities involving fossils, dinosaur evidence, and the detective work behind palaeontology.",
        ],
        "details": [
            "Activities are designed to mix learning with imagination, giving children plenty of chances to investigate rather than simply listen.",
            "The day focuses on evidence and discovery, helping children understand how scientists can learn so much from fragments left behind in rock.",
            "Expect ancient bones, big questions, and at least one very serious discussion about favourite dinosaurs.",
        ],
        "closings": [
            "Bring your curiosity and prepare to dig into the prehistoric past.",
            "Choose your favourite dinosaur carefully; somebody will almost certainly ask.",
        ],
    },

    "mini_makers": {
        "category": "Family",
        "openings": [
            "Give young creators a table full of materials and see where their imagination takes them.",
            "Set young makers loose on a collection of creative materials in a workshop where inventing is more important than following one perfect example.",
            "Bring curious hands and big ideas to a family making session designed for building, decorating, and experimenting.",
        ],
        "activities": [
            "Children will work through a selection of small making activities involving building, decorating, designing, and experimenting with different materials.",
            "Try a mixture of simple craft and construction challenges that encourage children to make choices and develop their own ideas.",
            "Young makers can cut, build, decorate, combine, and redesign materials while creating a collection of small projects to take home.",
        ],
        "details": [
            "The session is designed to encourage creativity without insisting that every project looks the same at the end.",
            "Friendly guidance is available whenever needed, but unusual ideas are very much encouraged.",
            "Expect glue, colour, concentration, and the proud presentation of something that may require a detailed explanation on the journey home.",
        ],
        "closings": [
            "Come ready to make, experiment, and give a few unusual ideas a chance.",
            "Bring your imagination and leave with something that did not exist when you arrived.",
        ],
    },

    "family_board_game_cafe": {
        "category": "Family",
        "openings": [
            "Settle around the table for an afternoon of board games designed for children, grown-ups, and anyone who takes tiny wooden pieces far too seriously.",
            "Swap the screens for cards, dice, boards, and a table full of family-friendly competition.",
            "Gather the family for a relaxed café session where choosing the next board game may be the hardest decision of the afternoon.",
        ],
        "activities": [
            "Choose from a range of quick games, family favourites, cooperative challenges, and friendly competitions while enjoying the relaxed café atmosphere.",
            "Try familiar favourites or discover something new, with games available for different ages, group sizes, and attention spans.",
            "Move between short challenges, cooperative games, and competitive favourites while staff help match families with something suitable to play.",
        ],
        "details": [
            "Staff can help explain unfamiliar games, so nobody needs to spend half an hour decoding a rulebook before starting.",
            "There is no pressure to know the games in advance; the aim is to sit down, play together, and perhaps discover a new favourite.",
            "The atmosphere is relaxed enough for beginners but competitive enough for anybody who insists they are only playing for fun right up until the final turn.",
        ],
        "closings": [
            "Pick a game, choose your team carefully, and remember that family harmony is technically more important than winning.",
            "Roll the dice, deal the cards, and try not to take the final score home with you.",
        ],
    },

    "campfire_stories": {
        "category": "Family",
        "openings": [
            "Gather around the fire as daylight fades for an evening of stories, imagination, and outdoor atmosphere.",
            "Pull up a seat by the campfire and settle in for a family evening where the flames provide the lighting and the stories provide everything else.",
            "As evening settles in, gather around the fire for stories shared beneath the open sky.",
        ],
        "activities": [
            "Listen to a mixture of folktales, funny stories, gentle adventures, and traditional campfire favourites told in a relaxed family-friendly setting.",
            "Storytellers will share a selection of family-friendly tales while the group settles around the fire and the evening grows darker.",
            "Enjoy spoken stories ranging from playful adventures to traditional favourites, all chosen to suit a family audience around the campfire.",
        ],
        "details": [
            "There will be time to settle in, warm up, and enjoy the simple pleasure of listening together without a screen in sight.",
            "The outdoor setting adds its own soundtrack, with crackling fire and evening noises making each tale feel a little more immediate.",
            "The stories stay family-friendly, with atmosphere coming from the setting, the storyteller, and everybody's imagination.",
        ],
        "closings": [
            "Bring something warm to wear and get comfortable while the fire crackles and the stories take over.",
            "Wrap up warm, settle by the fire, and let the next story begin.",
        ],
    },

    "family_movie_afternoon": {
        "category": "Family",
        "openings": [
            "Make an afternoon of the cinema with a family-friendly screening chosen for younger viewers and the grown-ups accompanying them.",
            "Settle into the cinema for an easy family afternoon built around a film everyone can enjoy together.",
            "Give the family a couple of hours on the big screen with a movie session chosen for younger audiences and their grown-ups.",
        ],
        "activities": [
            "Settle into the theatre with snacks, comfortable seats, and a film everyone can enjoy together on the big screen.",
            "Find your seats, get comfortable, and enjoy a family-friendly feature in an easygoing afternoon screening.",
            "Enjoy a carefully selected family film on the big screen with a relaxed atmosphere suited to children and accompanying adults.",
        ],
        "details": [
            "It is a simple shared outing for families who want a cinema trip without making a whole evening of it.",
            "No elaborate planning is required; just arrive, settle in, and let the film provide the adventure for a while.",
            "It is a straightforward chance to enjoy a story together somewhere considerably larger than the television at home.",
        ],
        "closings": [
            "Find your seats, silence the phones, and let somebody else provide the adventure for a couple of hours.",
            "Grab the snacks, settle in, and enjoy the show together.",
        ],
    },

    "junior_art_adventure": {
        "category": "Family",
        "openings": [
            "Give young artists the freedom to experiment with colour, shape, texture, and plenty of creative materials.",
            "Turn the art table over to young imaginations for a session filled with colour, making, and experimentation.",
            "Bring young creators along for an art session where trying ideas matters far more than making every picture look the same.",
        ],
        "activities": [
            "Children will try a mixture of drawing, painting, collage, and simple craft activities designed to encourage imagination rather than produce identical finished pieces.",
            "Experiment with drawing, paint, collage, colour, and texture through a collection of guided activities with plenty of room for individual ideas.",
            "Young artists can move between creative activities that introduce different materials and techniques without prescribing one correct finished result.",
        ],
        "details": [
            "Friendly guidance is available throughout, but there is plenty of room for individual ideas to take over.",
            "The emphasis is on enjoying the creative process, trying new materials, and giving unusual ideas somewhere to go.",
            "Expect colour, concentration, and at least one creation that immediately receives a very specific explanation from its artist.",
        ],
        "closings": [
            "Wear something that can survive a little artistic enthusiasm and prepare to leave with at least one masterpiece destined for the fridge door.",
            "Bring your imagination, expect a little mess, and take home something proudly original.",
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

    "live_acoustic_night": {
        "category": "Music & Entertainment",
        "openings": [
            "Settle in for a relaxed evening of live acoustic music performed up close in an intimate setting.",
            "Get comfortable for a close-up night of live music where voice and instrument take centre stage.",
            "Spend the evening with local musicians, warm atmosphere, and songs performed without the layers of a full production.",
        ],
        "activities": [
            "Local musicians will share familiar favourites alongside original songs, all arranged for a simple acoustic setup.",
            "Hear talented performers reinterpret familiar songs alongside original material in a close, informal setting.",
            "Enjoy acoustic sets from local performers, with the smaller arrangement leaving plenty of space for the songs themselves.",
        ],
        "details": [
            "The intimate setup keeps the focus firmly on the performers and gives every song a little more room to breathe.",
            "Songs often land differently when the arrangement is stripped back, giving lyrics and melodies more room to breathe.",
            "The relaxed atmosphere makes it easy to settle in, discover new performers, and simply enjoy the music at close range.",
            "It is a night designed for listening rather than spectacle, with the songs doing most of the work.",
        ],
        "closings": [
            "Grab a drink, find a comfortable seat, and let the music carry the evening.",
            "Listen closely and enjoy the songs without anything getting in their way.",
        ],
    },

    "indie_unplugged": {
        "category": "Music & Entertainment",
        "openings": [
            "Discover emerging indie artists in a night built around stripped-back performances and original material.",
            "Spend the evening hearing indie songs reduced to their essentials in an intimate unplugged setting.",
            "Get closer to the songs themselves with a night of acoustic performances from emerging indie artists.",
        ],
        "activities": [
            "Hear original songs and reworked arrangements performed without the layers of a full electric setup.",
            "A changing line-up of indie performers will share acoustic versions of their own material and carefully chosen influences.",
            "Discover new artists as they bring original songs to the room in stripped-back, close-up performances.",
        ],
        "details": [
            "Without the weight of a full production, the songwriting and performance sit right at the front of the experience.",
            "Expect new voices, unexpected arrangements, and at least one track you end up searching for on the way home.",
            "The smaller setting gives emerging artists room to experiment and the audience a chance to hear the detail in each song.",
            "It is an easy way to discover artists before everybody else starts claiming they knew them first.",
        ],
        "closings": [
            "Come curious and leave with at least one new artist on your radar.",
            "Find a seat, keep an open mind, and see which new song follows you home.",
        ],
    },

    "jazz_under_the_stars": {
        "category": "Music & Entertainment",
        "openings": [
            "Spend the evening beneath the night sky with live jazz providing the soundtrack.",
            "Settle in outdoors for an atmospheric night of live jazz beneath the stars.",
            "Let the evening slow down with live jazz, open air, and a setting made for lingering a little longer.",
        ],
        "activities": [
            "A talented group of musicians will perform classic standards, original arrangements, and plenty of improvisation.",
            "Hear experienced players move between familiar jazz favourites and spontaneous musical conversations.",
            "Enjoy a varied live set where standards and original pieces leave plenty of room for improvisation.",
        ],
        "details": [
            "The outdoor setting gives the music an extra sense of occasion without losing the relaxed feel of the evening.",
            "No two pieces will unfold in quite the same way twice, which is part of the pleasure of hearing jazz live.",
            "Whether you already love jazz or simply want to hear something different, the atmosphere is designed to be welcoming rather than formal.",
            "Expect expressive playing, shifting rhythms, and those unpredictable moments that only really happen in a live performance.",
        ],
        "closings": [
            "Bring a drink, settle in beneath the night sky, and let the music stretch into the evening.",
            "Find a comfortable spot and enjoy the sound of live jazz after dark.",
        ],
    },

    "comedy_club_night": {
        "category": "Music & Entertainment",
        "openings": [
            "Settle in for a night of stand-up comedy, sharp observations, and several opinions nobody requested.",
            "Leave your serious face at home for an evening built around live stand-up and a rotating line-up of comedians.",
            "Prepare for a night of stories, one-liners, awkward truths, and performers willing to say the quiet part into a microphone.",
        ],
        "activities": [
            "A varied line-up of comedians will take to the stage with stories, observations, one-liners, and unpredictable material.",
            "Each performer gets their turn at the microphone, bringing a different style of stand-up to the room.",
            "Expect several comedians, fresh material, and the occasional moment of audience interaction nobody planned for.",
        ],
        "details": [
            "The evening can move from clever to ridiculous in the space of a microphone handover.",
            "Some jokes will be carefully crafted, some gloriously silly, and at least one may make you question why you laughed.",
            "The atmosphere is informal, the line-up is varied, and very little is improved by sitting in the front row looking nervous.",
            "It is the kind of night where the safest plan is to grab a drink and let somebody else do the talking.",
        ],
        "closings": [
            "Grab a drink, take a seat, and prepare to laugh at things you probably should not repeat at work.",
            "Find your seat, settle in, and hope the comedian does not ask what you do for a living.",
        ],
    },

    "vinyl_dj_night": {
        "category": "Music & Entertainment",
        "openings": [
            "Spend the night listening to music the old-fashioned way, one record at a time.",
            "Let the needle drop on an evening built entirely around vinyl, deep cuts, and a dance floor ready for whatever comes next.",
            "Step into a night where the decks are loaded with records and every track begins with a needle finding the groove.",
        ],
        "activities": [
            "DJs will build their sets entirely from vinyl, moving through carefully chosen tracks, familiar favourites, and unexpected finds.",
            "Hear selectors move between records by hand, shaping the night one side, one groove, and one well-timed choice at a time.",
            "Expect a vinyl-only set that mixes recognisable tracks with deeper cuts and records you may never have heard before.",
        ],
        "details": [
            "A little surface crackle is part of the charm when every track is arriving from an actual record rather than a playlist.",
            "The night is built for dancing, listening, and occasionally wondering what obscure record just changed the whole room.",
            "There is no algorithm choosing what comes next; the direction of the set belongs entirely to the person behind the decks.",
            "Familiar songs sit alongside unexpected finds, giving the evening the feel of somebody sharing a very large record collection at full volume.",
        ],
        "closings": [
            "Find a space on the dance floor, let the needle drop, and see where the next side takes the room.",
            "Come for the records, stay for the next track, and try not to ask the DJ what is coming up.",
        ],
    },

    "battle_of_the_bands": {
        "category": "Music & Entertainment",
        "openings": [
            "Watch local bands go head-to-head in a live competition where every act gets a chance to own the stage.",
            "Turn the volume up for a night of competing bands, short sets, and plenty of reasons for the crowd to pick a favourite.",
            "Several local bands, one stage, and a limited amount of time to make the biggest possible impression.",
        ],
        "activities": [
            "Each band will perform a short live set before the next act takes over, with judges and crowd reaction helping decide the winner.",
            "Hear a succession of local acts bring different sounds to the same stage before the strongest performance is chosen at the end of the night.",
            "Bands will compete through tightly timed sets, giving the audience a fast-moving showcase of different styles and personalities.",
        ],
        "details": [
            "Expect loud guitars, big performances, nervous introductions, and at least one act treating twenty minutes like a stadium headline slot.",
            "The changing line-up keeps the room moving, with every band having to win over an audience that may have arrived supporting somebody else.",
            "Part competition and part showcase, the night is as much about discovering local music as it is about deciding who wins.",
            "Crowd energy matters, so quietly appreciating your favourite band from the back of the room may not be enough.",
        ],
        "closings": [
            "Pick your favourite and make enough noise to ensure they know it.",
            "Choose your side, get close to the stage, and see which band takes the night.",
        ],
    },

    "silent_disco": {
        "category": "Music & Entertainment",
        "openings": [
            "Put on a pair of wireless headphones and step onto a dance floor where everybody may be hearing something different.",
            "Choose your channel, turn up the headphones, and enter a disco that becomes wonderfully strange the moment you take them off.",
            "Spend the night switching between DJs through wireless headphones while the room dances to several soundtracks at once.",
        ],
        "activities": [
            "Multiple DJs will broadcast at the same time, letting you switch between music styles whenever the current track stops doing the job.",
            "Use the controls on your headphones to move between competing DJ channels without ever leaving the dance floor.",
            "Pick a channel, compare it with whatever your friends are hearing, and switch whenever another DJ looks suspiciously more popular.",
        ],
        "details": [
            "Take the headphones off for a moment and the packed dance floor becomes a room full of people enthusiastically moving to near silence.",
            "Different channels mean friends can stand beside each other while dancing to completely different songs.",
            "The freedom to switch music instantly makes the night feel less like one DJ set and more like carrying several clubs around on your head.",
            "Half the entertainment comes from the music and the other half from trying to work out why somebody nearby is singing a completely different chorus.",
        ],
        "closings": [
            "Pick a channel, turn it up, and try not to judge whatever your friends are clearly listening to instead.",
            "Grab your headphones, choose a soundtrack, and let everybody else worry about their own channel.",
        ],
    },

    "open_mic_night": {
        "category": "Music & Entertainment",
        "openings": [
            "Take a seat for an evening where the stage belongs to whoever is brave enough to step up next.",
            "Expect the unexpected at an open mic night where the next performer could bring a song, a poem, a joke, or something nobody predicted.",
            "Spend the evening supporting performers who have decided tonight is the night to give the stage a go.",
        ],
        "activities": [
            "Singers, musicians, poets, comedians, and other performers will each get a short turn in front of the room.",
            "Watch a changing line-up of performers share songs, spoken word, comedy, and whatever else fits into their time at the microphone.",
            "The stage stays open to a mixture of new and experienced performers, making the running order deliberately difficult to predict.",
        ],
        "details": [
            "Some acts may be polished while others are trying something publicly for the first time, and that uncertainty is part of the appeal.",
            "The audience is there to support the people willing to step up, so first attempts are just as welcome as confident performances.",
            "No two open mic nights are quite the same because the character of the evening depends entirely on who signs up.",
            "It is part showcase, part experiment, and occasionally the beginning of somebody realising they want to do this again.",
        ],
        "closings": [
            "Come to perform or simply support the people who decided tonight was the night to give it a go.",
            "Take a seat, cheer generously, and see who steps up next.",
        ],
    },

    "comedy_improv_evening": {
        "category": "Music & Entertainment",
        "openings": [
            "Spend an evening watching quick-thinking performers turn ideas invented on the spot into something nobody could have rehearsed.",
            "Forget the script, because this comedy night is built around performers making everything up as they go.",
            "Settle in for an improv show where audience suggestions can send the performers somewhere nobody expected.",
        ],
        "activities": [
            "Performers will use audience suggestions to create scenes, characters, and comedy games without a prepared script.",
            "Watch the cast turn random prompts into fast-moving scenes while trying to support whatever increasingly strange idea appears next.",
            "A mixture of improv games and longer scenes will be created live, with the audience helping provide the starting points.",
        ],
        "details": [
            "With no script to fall back on, every scene can veer somewhere unexpected and no performance can be repeated exactly.",
            "Quick thinking, teamwork, and complete commitment to a terrible idea are all useful skills once a scene has started.",
            "The performers usually discover where the scene is going at roughly the same moment the audience does.",
            "Even impossible suggestions can become fuel once the performers decide to commit to them.",
        ],
        "closings": [
            "Bring a suggestion and enjoy watching somebody else work out what to do with it.",
            "Take a seat and enjoy a comedy show that nobody in the room has seen before, including the cast.",
        ],
    },

    "tribute_night_live": {
        "category": "Music & Entertainment",
        "openings": [
            "Celebrate the songs of a much-loved artist with a full live tribute performance built around the hits people came to hear.",
            "Turn the evening into a proper singalong with a live tribute act recreating the songs, sound, and energy of a favourite artist.",
            "Spend the night revisiting familiar hits through a live tribute show designed to feel much closer to a concert than a covers set.",
        ],
        "activities": [
            "A dedicated tribute act will recreate familiar tracks with a live-band sound, stage presence, and plenty of crowd interaction.",
            "Hear a full set of recognisable songs performed live with arrangements designed to capture the character of the original artist.",
            "The show brings together the biggest crowd favourites, deeper cuts, and the kind of choruses everybody suddenly remembers word for word.",
        ],
        "details": [
            "Expect big choruses, familiar introductions, and plenty of opportunities to sing along without being remotely subtle about it.",
            "The aim is to capture the atmosphere of a live concert rather than simply reproduce the songs one after another.",
            "Long-time fans can enjoy the details while casual listeners can rely on the songs everybody knows by the first few seconds.",
            "It is an unapologetic celebration of familiar music, complete with the collective realisation that everybody remembers far more lyrics than expected.",
        ],
        "closings": [
            "Bring your friends and prepare to know far more lyrics than you thought you remembered.",
            "Warm up your singing voice and settle in for a night of favourites played loud and live.",
        ],
    },

    "leathercraft_beginners": {
        "category": "Workshops",
        "openings": [
            "Spend a few hours discovering the satisfying process of turning a simple piece of leather into something useful and entirely your own.",
            "Get hands-on with leathercraft in a beginner-friendly workshop built around traditional tools, careful stitching, and a practical project.",
            "Start with a plain piece of leather and learn how cutting, shaping, and stitching can turn it into something made to last.",
        ],
        "activities": [
            "Learn the basics of cutting, punching, stitching, and finishing before creating a small beginner-friendly project to take home.",
            "Practise measuring, marking, punching, and hand-stitching leather before bringing the techniques together in your own project.",
            "An instructor will introduce the essential tools and show you how to prepare, join, and finish leather safely and neatly.",
        ],
        "details": [
            "The workshop is practical from the start, with guidance available as you get used to the tools and materials.",
            "No previous experience is required, and the project is chosen to give beginners a useful introduction without rushing the process.",
            "Working slowly and accurately matters more than working quickly, particularly once the stitching begins to pull the piece together.",
            "Expect concentration, a few stubborn stitches, and the very specific satisfaction of realising you actually made that.",
        ],
        "closings": [
            "Bring your curiosity and leave with something handmade, useful, and unmistakably yours.",
            "Take your time, trust the process, and see what a few simple tools can do to a piece of leather.",
        ],
    },

    "intro_wood_carving": {
        "category": "Workshops",
        "openings": [
            "Pick up the carving tools and discover how a plain piece of wood can gradually turn into something with shape, texture, and character.",
            "Spend a quiet, hands-on session learning how controlled cuts can transform a simple block of wood.",
            "Get introduced to wood carving with a beginner-friendly project designed to teach control, patience, and safe tool use.",
        ],
        "activities": [
            "Learn how to work safely with basic carving techniques before practising controlled cuts on a small project of your own.",
            "An instructor will demonstrate grip, cutting direction, and simple shaping techniques before you begin carving your own piece.",
            "Practise making clean, deliberate cuts while learning how grain direction and tool angle affect the way the wood responds.",
        ],
        "details": [
            "The session is designed for beginners, so the emphasis is on patience, technique, and learning how the material responds beneath the blade.",
            "Progress comes from small controlled cuts rather than force, making concentration considerably more useful than speed.",
            "You will have guidance throughout while still getting plenty of uninterrupted time to develop a feel for the tools.",
            "Expect wood shavings, steady hands, and the strange pleasure of spending an afternoon deliberately removing tiny pieces of something.",
        ],
        "closings": [
            "Take it slowly, follow the grain, and see what begins to emerge from the wood.",
            "Bring your patience and leave with a first carving and a better sense of how deliberate cuts shape the wood.",
        ],
    },

    "beginners_photography_walk": {
        "category": "Workshops",
        "openings": [
            "Take your camera out into the local area and discover how composition, light, perspective, and timing can completely change an ordinary scene.",
            "Turn familiar streets into a practical photography classroom during a walk built around seeing ordinary places differently.",
            "Grab your camera and spend a morning learning how small choices behind the lens can make a much stronger photograph.",
        ],
        "activities": [
            "Work through a series of practical photography challenges while an experienced photographer explains techniques you can use immediately.",
            "Explore the local area while experimenting with framing, viewpoint, available light, and simple camera settings.",
            "Put composition and lighting ideas into practice as you stop at different locations and try several ways of photographing the same scene.",
        ],
        "details": [
            "The emphasis is on taking pictures rather than sitting through technical lectures, so you will have plenty of opportunities to experiment as you walk.",
            "The session is suitable for beginners and focuses on practical decisions you can continue using long after the walk ends.",
            "You do not need expensive equipment; understanding where to stand and what to include can matter far more than the camera in your hand.",
            "Looking for photographs tends to make details, reflections, shapes, and light much harder to ignore afterwards.",
        ],
        "closings": [
            "Bring any camera you are comfortable using and prepare to notice details you probably walked past on the way there.",
            "Charge the battery, clear a little memory-card space, and start looking at familiar places with a photographer's eye.",
        ],
    },

    "creative_writing_evening": {
        "category": "Workshops",
        "openings": [
            "Settle in for an evening of prompts and practical exercises built to get words moving onto the page.",
            "Give the blank page somewhere to start with a relaxed creative writing session built around prompts, characters, and new ideas.",
            "Spend an evening experimenting with words in a supportive workshop where unfinished ideas are more than welcome.",
        ],
        "activities": [
            "Explore character, setting, dialogue, and different ways of approaching a blank page while sharing techniques with other writers in a relaxed setting.",
            "Work through short writing challenges that generate ideas, sharpen description, and experiment with voice and dialogue.",
            "Use guided prompts to create scenes, characters, and fragments of stories before deciding which ideas deserve a little more time.",
        ],
        "details": [
            "There is no expectation that you arrive with a finished idea, and nobody is required to produce the opening chapter of the next literary phenomenon before going home.",
            "The emphasis is on generating material and trying techniques rather than polishing every sentence before moving on.",
            "Writers of different experience levels are welcome, and sharing work is encouraged without being compulsory.",
            "Sometimes the most useful part of a writing session is discovering that the idea you nearly ignored is the one that keeps growing.",
        ],
        "closings": [
            "Bring something to write with and give yourself permission to follow whatever strange direction the first sentence chooses.",
            "Come with a notebook, a laptop, or just an empty page and see what decides to appear on it.",
        ],
    },

    "intro_3d_printing": {
        "category": "Workshops",
        "openings": [
            "Discover how a digital model becomes a physical object in this beginner-friendly introduction to 3D printing.",
            "Take the mystery out of 3D printing by following a model from the computer screen to the finished object.",
            "See additive manufacturing in action during a practical introduction to modelling, slicing, and printing layer by layer.",
        ],
        "activities": [
            "Learn how to prepare and slice a model, choose sensible settings, and avoid turning a promising print into a mysterious box quietly manufacturing plastic spaghetti.",
            "Follow the workflow from digital model to slicer settings and printer setup before seeing how the finished object is built one layer at a time.",
            "Explore the software and printer controls used to prepare a simple model, then watch the machine translate those instructions into a physical print.",
        ],
        "details": [
            "No previous 3D modelling or printing experience is required, and the session focuses on the practical concepts beginners need first.",
            "You will learn why orientation, supports, layer height, and a well-prepared model can make the difference between a clean print and a failed one.",
            "Seeing the whole process makes the printer feel much less mysterious than simply watching an object appear on the build plate.",
            "By the end, the printer should feel considerably less like a mysterious box quietly manufacturing plastic spaghetti.",
        ],
        "closings": [
            "Follow the layers from screen to print and leave with a much clearer idea of what the machine is doing.",
            "Bring your curiosity and discover what has to happen before the printer gets to do the impressive-looking part.",
        ],
    },

    "build_your_own_terrarium": {
        "category": "Workshops",
        "openings": [
            "Create a miniature landscape of your own while learning how to build and care for a simple terrarium.",
            "Build a tiny planted world inside glass in a relaxed workshop combining horticulture with just enough creative landscaping.",
            "Spend a few peaceful hours assembling plants, soil, stone, and texture into a terrarium designed to keep growing after the workshop ends.",
        ],
        "activities": [
            "Layer drainage materials, soil, plants, stones, and decorative elements before arranging everything inside a glass container.",
            "Learn how to prepare the container, position suitable plants, and finish the surface with stones and decorative details.",
            "Work through the terrarium layer by layer, choosing plants and arranging them into a small landscape of your own design.",
        ],
        "details": [
            "The workshop covers the basics of choosing suitable plants and maintaining the little ecosystem once you take it home.",
            "You will learn how light, moisture, drainage, and plant choice affect how well the terrarium settles in afterwards.",
            "The process is beginner-friendly and leaves plenty of room to rearrange things until the miniature landscape feels right.",
            "There is plenty of room for creativity, whether your finished terrarium looks like a peaceful forest floor or a tiny world with suspiciously elaborate landscaping.",
        ],
        "closings": [
            "Build it, plant it, and take home a small landscape that continues changing long after the workshop ends.",
            "Bring your imagination and leave with a tiny ecosystem occupying considerably less space than a garden.",
        ],
    },

    "digital_illustration_basics": {
        "category": "Workshops",
        "openings": [
            "Pick up a stylus and explore the fundamentals of drawing and painting digitally.",
            "Turn the screen into a sketchbook during a beginner-friendly introduction to digital illustration tools and techniques.",
            "Explore digital drawing from the first brush stroke to a finished illustration in a practical session for curious beginners.",
        ],
        "activities": [
            "Learn how layers, brushes, colour, selection tools, and simple shortcuts can make the creative process more flexible without replacing the need for actual ideas.",
            "Work through practical exercises using brushes, layers, selections, and colour before combining the techniques in an illustration of your own.",
            "Experiment with digital brushes, layer organisation, colour choices, and editing tools while building up a simple piece step by step.",
        ],
        "details": [
            "No previous digital-art experience is required, and the exercises are designed to make the software feel less intimidating very quickly.",
            "Layers make it easier to experiment without committing every decision permanently, which is particularly useful while learning.",
            "The focus stays on practical creative choices rather than trying to memorise every button the software happens to contain.",
            "Undo is available for those moments when artistic confidence gets slightly ahead of artistic accuracy.",
        ],
        "closings": [
            "Bring your ideas, get comfortable with the tools, and leave with a digital piece you built yourself.",
            "Pick up the stylus, trust the undo button when necessary, and see what takes shape on screen.",
        ],
    },

    "furniture_restoration": {
        "category": "Workshops",
        "openings": [
            "Give tired furniture a second chance while learning the basics of assessing, preparing, repairing, and refinishing a piece.",
            "Discover how careful restoration can revive an old piece of furniture without sanding away everything that gave it character.",
            "Look beyond scratches and worn finishes in a practical workshop about deciding what old furniture actually needs before reaching for the tools.",
        ],
        "activities": [
            "Explore techniques for cleaning surfaces, dealing with minor damage, removing old finishes, and applying a fresh one without erasing the character that made the piece worth saving.",
            "Learn how to assess a piece before working through basic cleaning, preparation, small repairs, and refinishing techniques.",
            "An instructor will demonstrate how to approach worn surfaces and minor damage before introducing beginner-friendly restoration and finishing methods.",
        ],
        "details": [
            "The workshop focuses on careful restoration rather than turning everything into something brand new.",
            "Understanding the existing material and finish helps you decide what should be repaired, refreshed, or simply left alone.",
            "The aim is to improve the piece while respecting the age, marks, and details that give it its individual character.",
            "A little patience and the right preparation can often rescue something that looked much closer to the tip than the living room.",
        ],
        "closings": [
            "Bring your curiosity and leave with a much better idea of what can be rescued before it gets sent to the tip.",
            "Learn to look past the worn surface and see what might still be worth saving underneath it.",
        ],
    },

    "natural_soap_making": {
        "category": "Workshops",
        "openings": [
            "Learn how handmade soap comes together from carefully measured ingredients in a practical beginner-friendly workshop.",
            "Turn oils, fragrance, colour, and careful measurements into a small batch of handmade soap of your own.",
            "Discover the process behind handmade soap in a workshop that combines precise measuring with plenty of room for colour and fragrance choices.",
        ],
        "activities": [
            "Explore the basic process, discover how colour and fragrance can be added, and create a small batch of soap to take away and cure at home.",
            "Follow the soap-making process step by step, from measuring ingredients safely to mixing, scenting, colouring, and pouring the finished batch into moulds.",
            "Learn how the ingredients are combined before experimenting with fragrance, colour, and simple finishing choices for your own batch.",
        ],
        "details": [
            "Safety and accurate measuring are explained clearly before the hands-on part begins, so you can concentrate on the creative side with confidence.",
            "No previous experience is required, but careful measurements matter because soap making is equal parts craft and chemistry.",
            "Your finished soap will need time to cure at home, giving the workshop a result that continues developing after the session ends.",
            "Expect interesting scents, satisfying moulds, and a new appreciation for something most of us normally use without giving it a second thought.",
        ],
        "closings": [
            "Choose your scent, measure carefully, and take home a batch that is entirely your own.",
            "Come ready to mix, pour, and leave with a much better understanding of what goes into an everyday bar of soap.",
        ],
    },

    "intro_screen_printing": {
        "category": "Workshops",
        "openings": [
            "Discover the wonderfully hands-on process of pushing ink through a screen and revealing a finished design underneath.",
            "Turn a simple design into a repeatable print during a practical introduction to screens, ink, pressure, and colour.",
            "Get hands-on with screen printing in an introductory session where the most satisfying moment arrives when the screen lifts away.",
        ],
        "activities": [
            "Learn how artwork is prepared, how the screen is used, and how pressure and ink placement affect the final print before creating a small set of your own.",
            "Work through the basic process of preparing a design, positioning the screen, applying ink, and pulling your own prints.",
            "Experiment with simple shapes, layers, and colour while learning how a screen turns the same design into a series of individual prints.",
        ],
        "details": [
            "The workshop leaves plenty of room to experiment with colour, shape, and layering while you build confidence with the technique.",
            "Small variations between prints are part of the process, so perfectly identical results are neither required nor especially interesting.",
            "You will have guidance throughout while still getting enough hands-on time to understand how pressure and ink affect the result.",
            "The best moment is still lifting the screen to see whether the idea in your head actually survived contact with reality.",
        ],
        "closings": [
            "Bring an idea, get a little inky, and leave with a set of prints you pulled yourself.",
            "Lay down the ink, lift the screen, and enjoy the reveal one print at a time.",
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



    "evening_street_food_tour": {
        "category": "Food & Drink",
        "openings": [
            "Come hungry and spend the evening discovering some of the most interesting food spots around the local area.",
            "Leave dinner plans at home and follow the flavours of the local street food scene instead.",
            "Turn an ordinary evening meal into a guided tour through some of the area's best independent food stops.",
        ],
        "activities": [
            "Follow your guide between independent stalls and vendors while sampling different dishes and hearing the stories behind them.",
            "Visit a selection of local food stops, taste a range of dishes, and meet some of the people responsible for making them.",
            "Move between carefully chosen street food locations while discovering ingredients, cooking styles, and local favourites along the way.",
        ],
        "details": [
            "The pace is relaxed, with plenty of time to taste, chat, and discover something you may never have ordered on your own.",
            "Each stop offers something a little different, so arriving with an open mind is almost as useful as arriving with an appetite.",
            "It is as much about discovering the people and places behind the food as it is about working your way through the samples.",
        ],
        "closings": [
            "Bring an appetite and prepare to leave with at least one new favourite.",
            "Come hungry and let the route decide what is for dinner.",
            "Follow the guide, trust your appetite, and save a little room for the final stop.",
        ],
    },

    "artisan_chocolate": {
        "category": "Food & Drink",
        "openings": [
            "Spend a deliciously hands-on session discovering how handmade chocolate is prepared, shaped, and decorated.",
            "If chocolate counts as a hobby, this workshop gives you an excellent excuse to take it more seriously.",
            "Step behind the finished box of chocolates and discover some of the craft involved in making the treats inside it.",
        ],
        "activities": [
            "Learn the basics of tempering, flavouring, and working with chocolate before creating a selection of treats of your own.",
            "Work with quality chocolate while practising simple techniques for shaping, decorating, and combining flavours.",
            "Follow demonstrations from the tutor before trying the techniques yourself and turning melted chocolate into finished pieces.",
        ],
        "details": [
            "No previous experience is required, and tasting the results is considered a perfectly reasonable part of the learning process.",
            "The session is practical from start to finish, with plenty of opportunity to experiment with decoration, texture, and flavour.",
            "You will leave with a better understanding of the process and, assuming restraint survives the workshop, some handmade chocolate too.",
        ],
        "closings": [
            "Bring your sweet tooth and expect to leave with both new skills and very little resistance to trying one more piece.",
            "Come ready to learn, create, and accept that quality control may require repeated tasting.",
            "Prepare to get wonderfully chocolatey and considerably better informed about what goes into each piece.",
        ],
    },

    "pasta_from_scratch": {
        "category": "Food & Drink",
        "openings": [
            "Forget the packet for an evening and learn how fresh pasta comes together from a handful of simple ingredients.",
            "Roll up your sleeves and discover how flour, eggs, and a little technique become fresh handmade pasta.",
            "Spend an evening learning one of those kitchen skills that looks far more mysterious before someone shows you how it works.",
        ],
        "activities": [
            "Make and knead your own dough before rolling, cutting, shaping, and cooking it under the guidance of an experienced tutor.",
            "Work through the process from mixing the dough to shaping and cooking your finished pasta, with practical guidance at each stage.",
            "Learn how to judge the dough, roll it to the right thickness, and turn it into fresh shapes ready for the pan.",
        ],
        "details": [
            "The techniques are designed to be easy to repeat at home once you understand how the dough should feel and behave.",
            "There is plenty of time to practise before sitting down to enjoy the finished result.",
            "Expect a relaxed, practical session where slightly uneven pasta still tastes considerably better than it looks.",
        ],
        "closings": [
            "Bring your appetite and prepare for flour to reach places flour was never invited to.",
            "Come hungry and leave knowing exactly what stands between a bag of flour and dinner.",
            "Make it, cook it, eat it, and decide whether packet pasta has been permanently demoted.",
        ],
    },

    "coffee_tasting": {
        "category": "Food & Drink",
        "openings": [
            "Slow down and discover just how different one cup of coffee can taste from another.",
            "Give your usual coffee order a little competition with a guided tasting built around beans, aroma, and flavour.",
            "Spend a session exploring coffee beyond the familiar morning cup and learn what makes different beans taste the way they do.",
        ],
        "activities": [
            "Sample a selection of beans from different origins while learning how roast level, processing, brewing, and growing conditions influence flavour and aroma.",
            "Taste several coffees side by side while your host explains how origin, roast, and preparation can change what ends up in the cup.",
            "Learn a simple approach to tasting coffee, then compare different examples while identifying aroma, acidity, sweetness, body, and finish.",
        ],
        "details": [
            "No specialist knowledge is required, and the tasting is designed to help you notice characteristics you may never have paid attention to before.",
            "Comparing coffees directly makes subtle differences much easier to spot than they are during a hurried morning brew.",
            "The aim is not to find one 'correct' flavour, but to understand why different coffees can produce such different experiences.",
        ],
        "closings": [
            "Your usual morning coffee may face considerably harsher judgement afterwards.",
            "Bring your curiosity and leave with a much more opinionated relationship with the coffee cupboard.",
            "Taste carefully, compare freely, and discover what you actually like in a cup.",
        ],
    },

    "bake_your_own_pizza": {
        "category": "Food & Drink",
        "openings": [
            "Roll up your sleeves and build a pizza from dough to oven.",
            "Turn pizza night into a hands-on workshop where the finished meal begins with the dough in front of you.",
            "Make dinner yourself in a workshop devoted to dough, sauce, toppings, and the very important business of getting pizza into an oven.",
        ],
        "activities": [
            "Learn how to prepare and stretch the base before adding sauce, toppings, and your own combination of flavours.",
            "Work through shaping the dough, building the pizza, and preparing it for the oven with guidance available throughout.",
            "Practise handling pizza dough before choosing your toppings and assembling a pizza exactly the way you want it.",
        ],
        "details": [
            "There is plenty of room for personal creativity and questionable topping decisions.",
            "The workshop is suitable for beginners and focuses on simple techniques you can use again at home.",
            "Once everything is assembled, the oven takes over and turns the afternoon's work into something considerably easier to eat.",
        ],
        "closings": [
            "Once the pizzas are baked, the difficult part begins: waiting long enough for yours to cool before eating it.",
            "Choose your toppings wisely, trust the oven, and arrive hungry.",
            "Make it your way and enjoy the considerable advantage of eating the final project.",
        ],
    },

    "local_food_market_walk": {
        "category": "Food & Drink",
        "openings": [
            "Explore the market through the food, produce, and people that give it its character.",
            "Take a slower walk through the local market and discover the traders, ingredients, and flavours hidden between the busiest stalls.",
            "See the market as more than somewhere to shop with a guided walk built around local produce and independent traders.",
        ],
        "activities": [
            "Wander between independent traders while sampling local specialities, seasonal ingredients, and products you might otherwise walk straight past.",
            "Meet stallholders, taste selected produce, and hear some of the stories behind the businesses that keep the market moving.",
            "Follow your guide through the market while discovering local ingredients, specialist traders, and a selection of things worth tasting along the way.",
        ],
        "details": [
            "It is part tasting tour, part local exploration, and an excellent excuse to leave lunch plans flexible.",
            "The route focuses on the people and produce of the market rather than treating it as a row of anonymous stalls.",
            "Expect a mixture of familiar favourites and ingredients you may have passed without ever knowing what to do with them.",
        ],
        "closings": [
            "Come curious, arrive hungry, and leave with a few new reasons to visit the market again.",
            "Bring an appetite and give the market permission to rearrange your lunch plans.",
            "Take your time, talk to the traders, and see what earns a place on your next shopping list.",
        ],
    },

    "seasonal_supper_club": {
        "category": "Food & Drink",
        "openings": [
            "Take a seat at a shared table for an evening built around ingredients at their best.",
            "Settle in for a supper club where the season decides what deserves a place on the menu.",
            "Spend the evening around a shared table enjoying a menu shaped by what is fresh, available, and worth eating right now.",
        ],
        "activities": [
            "Enjoy a specially prepared multi-course menu showcasing seasonal produce and the ideas of the kitchen team.",
            "Work your way through several courses designed around ingredients chosen for the time of year.",
            "Let the kitchen guide the evening with a sequence of dishes that make the most of the season's produce.",
        ],
        "details": [
            "The relaxed supper-club setting encourages conversation and gives the meal a more intimate feel than a traditional restaurant visit.",
            "The exact menu can change with availability, making the season part of the experience rather than simply a label on it.",
            "There is no need to know what each course will be before arriving; part of the appeal is letting the kitchen make that decision for you.",
        ],
        "closings": [
            "Arrive curious, settle in, and let the kitchen decide what the season has brought to the table.",
            "Take your seat, meet the table, and see what the season tastes like tonight.",
            "Come hungry and leave the menu planning to somebody else for the evening.",
        ],
    },

    "dessert_decorating": {
        "category": "Food & Drink",
        "openings": [
            "Turn simple desserts into something worthy of a display case in a practical decorating workshop for beginners.",
            "Spend an afternoon learning how a few decorating techniques can transform a plain dessert into something made to be noticed.",
            "Bring a steady hand and a sweet tooth to a workshop built around piping, finishing, colour, and presentation.",
        ],
        "activities": [
            "Learn piping, finishing, presentation, and decorative techniques before applying them to a selection of sweet creations of your own.",
            "Practise beginner-friendly decorating techniques before combining them on desserts you can style and finish yourself.",
            "Experiment with piping, texture, colour, and finishing touches while learning how to make desserts look as considered as they taste.",
        ],
        "details": [
            "There is plenty of room to experiment with colour, texture, and style, and absolute perfection is not a requirement.",
            "The session focuses on techniques you can reuse at home rather than expecting professional results on the first attempt.",
            "Small mistakes are remarkably easy to forgive when the practice material happens to be dessert.",
        ],
        "closings": [
            "Anything that looks less than flawless has the useful advantage of still being dessert.",
            "Decorate boldly, taste responsibly, and remember that icing can solve a surprising number of problems.",
            "Bring your creativity and leave with techniques worth trying again the next time cake appears.",
        ],
    },

    "world_street_food_festival": {
        "category": "Food & Drink",
        "openings": [
            "Take a trip around the world without leaving the festival square, with street food inspired by cuisines from across the globe.",
            "Come hungry to a festival where choosing what to eat is considerably harder than finding something tempting.",
            "Let the festival square become your menu for the day, with stalls serving flavours and dishes inspired by food traditions from around the world.",
        ],
        "activities": [
            "Wander between vendors, sample different dishes, and discover everything from familiar favourites to something entirely new.",
            "Build your own route through the stalls, trying small dishes and snacks from a wide range of cuisines and cooking styles.",
            "Explore a lively collection of food stalls while choosing your own combination of dishes, flavours, and sweet treats.",
        ],
        "details": [
            "The atmosphere is lively and informal, so you can build your own menu one small dish at a time.",
            "With so many stalls competing for attention, sharing dishes is an excellent strategy for anybody unwilling to choose only one.",
            "The event is designed for grazing, discovering, and returning to the stall you spent twenty minutes insisting you were finished with.",
        ],
        "closings": [
            "Come hungry, bring friends, and accept early that choosing just one stall was never going to happen.",
            "Follow the aromas, split a few dishes, and make a day of eating your way around the square.",
            "Bring an appetite and enough indecision to justify trying several things.",
        ],
    },

    "great_afternoon_tea": {
        "category": "Food & Drink",
        "openings": [
            "Settle in for a traditional afternoon tea served with all the little details that make it feel like an occasion.",
            "Take the afternoon slowly with tiered stands, pots of tea, and a table designed for lingering rather than rushing.",
            "Give the afternoon a little ceremony with a classic spread of savouries, scones, cakes, and freshly poured tea.",
        ],
        "activities": [
            "Enjoy a selection of sandwiches, freshly baked scones, cakes, pastries, and pots of tea presented across a classic tiered stand.",
            "Work your way from savoury finger sandwiches through warm scones and into a final tier of cakes and pastries.",
            "Choose your tea, settle at the table, and enjoy a traditional spread served in the unhurried style afternoon tea deserves.",
        ],
        "details": [
            "The pace is deliberately unhurried, leaving plenty of time to chat, refill the teapot, and decide which cake deserves the final space.",
            "Part of the pleasure is taking your time, particularly when another pot of tea and one remaining pastry are still negotiating for attention.",
            "There is no need to turn the occasion formal unless you want to; the important requirement is leaving room for the sweet tier.",
        ],
        "closings": [
            "Dress it up or keep it relaxed, but definitely arrive with room for cake.",
            "Refill the pot, settle the jam-and-cream debate however you see fit, and enjoy the afternoon.",
            "Take your time, pour another cup, and do not underestimate the final tier.",
        ],
    },

    "last_showing": {
        "category": "Not For the Faint of Heart",
        "openings": [
            "The old picture house closed years ago, but tonight one projector is running again.",
            "The cinema should be empty, the screen should be dark, and yet somebody has scheduled one final showing.",
            "Take your seat in a picture house that has not welcomed an audience for years and try not to ask who started the projector.",
        ],
        "activities": [
            "Move through empty auditoriums, forgotten projection rooms, and staff corridors while fragments of an unfinished film begin appearing around you.",
            "Follow clues hidden among old reels, abandoned seats, and projection equipment as the story behind the cinema's final screening slowly comes into focus.",
            "Explore the closed picture house after hours, tracing a trail that leads from the auditorium to places the audience was never supposed to see.",
        ],
        "details": [
            "The experience reveals its story in pieces, with each new fragment raising slightly less comfortable questions about why the cinema closed.",
            "Some scenes appear to belong to the unfinished film. Others are harder to place.",
            "The building is quiet enough that every mechanical click from the projection booth feels much louder than it should.",
            "Staying until the credits feels like the obvious thing to do, although nobody has promised there will be credits.",
        ],
        "closings": [
            "Stay until the screen goes dark, but do not assume that means the showing is over.",
            "Take your seat, watch carefully, and try not to notice what changes between one frame and the next.",
        ],
    },

    "after_midnight": {
        "category": "Not For the Faint of Heart",
        "openings": [
            "Most of the city has gone home, the shutters are down, and the streets have become much quieter than they should be.",
            "Midnight has passed, the crowds have vanished, and the old district no longer feels arranged for ordinary visitors.",
            "Follow the city after midnight, when familiar streets begin behaving as though they belong to somebody else.",
        ],
        "activities": [
            "Follow a late-night route through the old district while strange encounters, unexplained clues, and fragments of local folklore begin to overlap.",
            "Move through empty squares, narrow streets, and overlooked corners while your group pieces together a story that seems to be unfolding slightly ahead of you.",
            "Trace a route across the sleeping city as messages, sightings, and carefully placed clues make familiar places feel increasingly unreliable.",
        ],
        "details": [
            "The experience relies on atmosphere and uncertainty rather than giving every strange moment a convenient explanation.",
            "The deeper into the night you travel, the harder it becomes to tell which moments were planned and which ones simply happened.",
            "Places that feel ordinary in daylight can become remarkably persuasive once the streets empty and the clocks stop being reassuring.",
            "Nobody is asking you to believe the stories. The route has a habit of making its own argument.",
        ],
        "closings": [
            "Midnight was only the beginning.",
            "Stay with the group and keep moving. The city can explain itself in the morning.",
        ],
    },

    "empty_room": {
        "category": "Not For the Faint of Heart",
        "openings": [
            "There is one room in the building that nobody seems willing to explain.",
            "The property has been empty for years, apart from the room everybody insists has always been empty.",
            "Every account of the building eventually mentions the same room, usually just before the person telling the story changes the subject.",
        ],
        "activities": [
            "Investigate the abandoned property through notes, objects, recordings, and traces left by the people who were there before you.",
            "Search the surrounding rooms for fragments of a story that repeatedly points back to one locked door at the centre of the experience.",
            "Piece together evidence scattered through the building until the only unanswered question is why one room was deliberately kept empty.",
        ],
        "details": [
            "Nothing you find quite agrees on what happened there, although every version seems unusually interested in the same door.",
            "The closer you get to the room, the less convincing the word 'empty' starts to sound.",
            "Some of the evidence appears old. Some of it does not.",
            "Opening the door is not technically compulsory, which somehow makes the decision worse.",
        ],
        "closings": [
            "When the door finally opens, remember that empty does not necessarily mean unoccupied.",
            "Find the room, learn why it was avoided, and decide whether you really needed the answer.",
        ],
    },

    "house_end_lane": {
        "category": "Not For the Faint of Heart",
        "openings": [
            "At the far end of a quiet lane stands a house that has been left alone for a very long time.",
            "The lane ends at a house nobody has lived in for years, although the building has never felt entirely abandoned.",
            "Walk past the last occupied house, keep following the lane, and eventually you will reach the one people prefer not to discuss.",
        ],
        "activities": [
            "Step inside and piece together the history of its former occupants through belongings, photographs, locked rooms, and things that appear to have been deliberately hidden.",
            "Explore the house room by room while family records, forgotten possessions, and sealed spaces gradually reveal a history that was never properly finished.",
            "Follow traces left by the people who lived there, moving deeper into a house where every room seems to preserve a slightly different version of the past.",
        ],
        "details": [
            "The story unfolds slowly, allowing ordinary domestic details to become considerably less ordinary once you understand what they are connected to.",
            "Some doors were locked for practical reasons. Others are harder to justify.",
            "The house does not need to jump out at you to feel occupied by its own history.",
            "By the time the final pieces fit together, leaving the photographs face-down may start to feel like a sensible tradition.",
        ],
        "closings": [
            "Houses remember more than people expect.",
            "Go inside, learn what happened there, and try not to give the house anything new to remember.",
        ],
    },

    "last_broadcast": {
        "category": "Not For the Faint of Heart",
        "openings": [
            "A local radio station stopped transmitting without warning decades ago. Tonight, the signal has returned.",
            "The station has been silent for years, but an old frequency has started broadcasting again after dark.",
            "Somewhere inside an abandoned radio studio, a transmission is repeating on equipment that should not have power.",
        ],
        "activities": [
            "Investigate old recordings, damaged equipment, unfinished broadcasts, and a repeating transmission that seems to contain something nobody remembers recording.",
            "Search the abandoned studio for tapes, logs, and fragments of the station's final night while the same unexplained signal continues in the background.",
            "Follow the trail from control room to recording booth as archived audio and a live frequency begin telling two versions of the same story.",
        ],
        "details": [
            "The clearer the signal becomes, the less certain it is that the broadcast was meant for the station's original listeners.",
            "Some voices belong to archived recordings. One of them appears to know you are listening now.",
            "Static is much easier to dismiss before it starts forming recognisable patterns.",
            "Turning the volume down helps less than you might expect.",
        ],
        "closings": [
            "Keep listening carefully. Something may be listening back.",
            "Find the source of the signal before the final transmission reaches the part nobody archived.",
        ],
    },

    "room_13": {
        "category": "Not For the Faint of Heart",
        "openings": [
            "The hotel has twelve rooms on the floor plan, twelve keys behind reception, and one door nobody acknowledges.",
            "There is no Room 13 on the booking system, although the thirteenth door is difficult to overlook once you know where to look.",
            "The hotel insists the numbering skips from twelve to fourteen. The corridor disagrees.",
        ],
        "activities": [
            "Explore the forgotten hotel corridors and uncover fragments of the room's history through guest records, abandoned luggage, and accounts that never quite agree.",
            "Trace old bookings, missing keys, and contradictory guest reports as your group works out why one room was removed from every official record.",
            "Move from reception into the closed upper floor, following a trail of hotel records that eventually leads to the door marked 13.",
        ],
        "details": [
            "The records disagree about who stayed there, how long they stayed, and whether they ever checked out.",
            "Staff stopped using the room number long before they stopped using the room.",
            "The key is still available, which raises the unhelpful question of why nobody has thrown it away.",
            "The door may be easy enough to open. Deciding how long to remain inside is another matter entirely.",
        ],
        "closings": [
            "Take the key, find the room, and try not to become part of the guest history.",
            "Check in if you must. Checking out is the more interesting part.",
        ],
    },

    "red_door": {
        "category": "Not For the Faint of Heart",
        "openings": [
            "Deep inside an unfamiliar building stands a red door with very clear instructions not to open it.",
            "The building contains dozens of doors. Only one is painted red, and everybody seems unusually interested in keeping it closed.",
            "You have been told where the red door is, why you should avoid it, and almost nothing else that could possibly make you less curious.",
        ],
        "activities": [
            "Follow a sequence of clues through connected rooms while uncovering why the door was sealed and why previous visitors were determined that it remain that way.",
            "Search the building for fragments of the door's history, solving clues that bring you steadily closer to the one place you were specifically told to avoid.",
            "Work through rooms, messages, and hidden evidence that gradually explain what lies beyond the red door without making opening it seem any wiser.",
        ],
        "details": [
            "Every answer brings you closer to opening it, which may not be the same thing as making progress.",
            "The instructions are surprisingly clear. Your reasons for ignoring them become less clear as the evening continues.",
            "The door has no obvious reason to feel different from any other door. It manages anyway.",
            "Eventually the only mystery left is whether knowing what is behind it will be worse than not knowing.",
        ],
        "closings": [
            "Find the truth behind the red door, then decide whether the handle really needs turning.",
            "You were warned not to open it. Consider this the second warning.",
        ],
    },

    "night_shift": {
        "category": "Not For the Faint of Heart",
        "openings": [
            "Report for duty at an office building long after the daytime staff have gone home.",
            "Your night shift begins in an empty office where the lights, phones, and security system are supposed to be the only things still working.",
            "Clock in after dark and take responsibility for a building that becomes much less ordinary once everybody else leaves.",
        ],
        "activities": [
            "Complete overnight checks, respond to unusual incidents, and follow security procedures as the building starts producing problems nobody included in the handover notes.",
            "Work through a list of routine night duties while phones ring from disconnected extensions and security logs record movement in empty departments.",
            "Follow the night-shift instructions across darkened offices, storage areas, and security stations as increasingly strange incidents demand a response.",
        ],
        "details": [
            "The rules are simple enough until the building begins creating situations the rules do not cover.",
            "Every logged incident has a time, a location, and no particularly satisfying explanation.",
            "The daytime staff left the building empty. The security system appears unconvinced.",
            "The most worrying entry on the attendance log is the one recorded before you arrived.",
        ],
        "closings": [
            "Finish the shift, follow procedure, and try not to wonder who clocked in before you.",
            "Morning is on the schedule. Your job is to make it that far.",
        ],
    },

    "something_woods": {
        "category": "Not For the Faint of Heart",
        "openings": [
            "A trail leads into the forest towards the place where several unexplained sightings were reported.",
            "Something has been seen in the woods often enough that somebody finally decided to follow the reports instead of dismissing them.",
            "Enter the forest after dark and follow a route towards the part of the woods local stories tend to describe very carefully.",
        ],
        "activities": [
            "Search for tracks, abandoned belongings, unusual markings, and signs that something has been moving through the area ahead of your group.",
            "Follow the trail deeper beneath the trees, examining fresh clues and trying to work out whether the sightings all point to the same thing.",
            "Move between reported sighting locations while collecting evidence that becomes harder to explain the further from the trailhead you travel.",
        ],
        "details": [
            "The deeper you go, the quieter the woods seem to become.",
            "Finding evidence is considerably less reassuring when the evidence looks fresh.",
            "Most woodland noises have perfectly ordinary explanations. The experience does not promise that all of them do.",
            "The route is easier to follow when you stop wondering whether something else is following it too.",
        ],
        "closings": [
            "Stay close, keep your torch pointed forward, and leave the woods with the same number of people you entered with.",
            "Follow the evidence as far as you dare. The trail back will still be there afterwards. Probably.",
        ],
    },

    "last_train_home": {
        "category": "Not For the Faint of Heart",
        "openings": [
            "The final train has already left, yet the departure board has just announced one more service.",
            "The station is closed, the platforms are empty, and a train that does not appear on the timetable is apparently on its way.",
            "You missed the last scheduled train home. Fortunately, the board has found another one. Unfortunately, nobody else seems pleased about it.",
        ],
        "activities": [
            "Follow the deserted platform as strange announcements, abandoned luggage, and fragments of a passenger's journey begin appearing around you.",
            "Search the closed station for clues about an unscheduled service while platform displays and announcements continue updating without any visible staff.",
            "Trace the story of a missing passenger through tickets, luggage, and station records as something approaches along a line that should no longer be in use.",
        ],
        "details": [
            "The timetable confirms the service exists only after you start looking for it.",
            "Every announcement sounds routine until you listen closely to the destination.",
            "The station remains empty, although the signs of another passenger become increasingly difficult to ignore.",
            "The timetable says this train goes home. It does not specify whose.",
        ],
        "closings": [
            "Wait for the train if you want. Just check the destination before you board.",
            "The service is approaching the platform. Whether it is your train is another question.",
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
    "Hidden History Walking Tour": "hidden_history",
    "After Dark City Tour": "after_dark_city",
    "Riverside Kayaking Experience": "riverside_kayaking",
    "Sunset Woodland Walk": "sunset_woodland",
    "Canal Canoeing Challenge": "canal_canoeing",
    "Sunrise Hilltop Hike": "sunrise_hilltop",
    "Urban Climbing Taster": "urban_climbing",
    "Orienteering Challenge": "orienteering_challenge",
    "Outdoor Survival Skills": "outdoor_survival",
    "The Great City Treasure Hunt": "city_treasure_hunt",

    # Arts & Culture
    "Beginner's Pottery Workshop": "beginner_pottery",
    "Introduction to Watercolour": "intro_watercolour",
    "Local Artists Exhibition Night": "local_artists_exhibition",
    "Printmaking for Beginners": "printmaking_beginners",
    "Museum After Hours": "museum_after_hours",
    "Life Drawing Evening": "life_drawing",
    "Poetry & Performance Night": "poetry_performance",
    "Independent Film Night": "independent_film",
    "Introduction to Calligraphy": "intro_calligraphy",
    "Candlelit Storytelling Evening": "candlelit_storytelling",

    # Family
    "Family Science Day": "family_science",
    "Outdoor Treasure Hunt": "family_treasure_hunt",
    "Junior Nature Explorers": "junior_nature_explorers",
    "Build Your Own Rocket": "build_your_own_rocket",
    "Dinosaur Discovery Day": "dinosaur_discovery",
    "Mini Makers Workshop": "mini_makers",
    "Family Board Game Café": "family_board_game_cafe",
    "Campfire Stories": "campfire_stories",
    "Family Movie Afternoon": "family_movie_afternoon",
    "Junior Art Adventure": "junior_art_adventure",

    # Food & Drink
    "Evening Street Food Tour": "evening_street_food_tour",
    "Local Food & Market Walk": "local_food_market_walk",
    "World Street Food Festival": "world_street_food_festival",
    "Artisan Chocolate Workshop": "artisan_chocolate",
    "Dessert Decorating Workshop": "dessert_decorating",
    "Pasta From Scratch": "pasta_from_scratch",
    "Coffee Tasting Experience": "coffee_tasting",
    "Bake Your Own Pizza": "bake_your_own_pizza",
    "Seasonal Supper Club": "seasonal_supper_club",
    "The Great Afternoon Tea": "great_afternoon_tea",

    # Music & Entertainment
    "Live Acoustic Night": "live_acoustic_night",
    "Indie Unplugged": "indie_unplugged",
    "Jazz Under the Stars": "jazz_under_the_stars",
    "Comedy Club Night": "comedy_club_night",
    "Vinyl DJ Night": "vinyl_dj_night",
    "Battle of the Bands": "battle_of_the_bands",
    "Silent Disco": "silent_disco",
    "Open Mic Night": "open_mic_night",
    "Comedy Improv Evening": "comedy_improv_evening",
    "Tribute Night Live": "tribute_night_live",

    # Workshops
    "Leathercraft for Beginners": "leathercraft_beginners",
    "Introduction to Wood Carving": "intro_wood_carving",
    "Beginner's Photography Walk": "beginners_photography_walk",
    "Creative Writing Evening": "creative_writing_evening",
    "Introduction to 3D Printing": "intro_3d_printing",
    "Build Your Own Terrarium": "build_your_own_terrarium",
    "Digital Illustration Basics": "digital_illustration_basics",
    "Furniture Restoration Basics": "furniture_restoration",
    "Natural Soap Making": "natural_soap_making",
    "Introduction to Screen Printing": "intro_screen_printing",

    # Not For the Faint of Heart
    "The Last Showing": "last_showing",
    "After Midnight": "after_midnight",
    "The Empty Room": "empty_room",
    "The House at the End of the Lane": "house_end_lane",
    "The Last Broadcast": "last_broadcast",
    "Room 13": "room_13",
    "The Red Door": "red_door",
    "The Night Shift": "night_shift",
    "Something in the Woods": "something_woods",
    "Last Train Home": "last_train_home",
}


EVENT_SPECIFIC_THEME_CATEGORIES = {
    "Adventure",
    "Arts & Culture",
    "Family",
    "Food & Drink",
    "Music & Entertainment",
    "Workshops",
    "Not For the Faint of Heart",
}


def generate_description(event_data):
    """Generate a varied description appropriate to the selected event."""

    theme = DESCRIPTION_THEME_BY_TITLE.get(event_data["name"])
    category = event_data["category"]

    # Categories upgraded to event-specific themes always use those themes.
    # Other categories keep the existing mixed theme/category behaviour until
    # their descriptions have been reviewed and upgraded in the same way.
    if theme and category in EVENT_SPECIFIC_THEME_CATEGORIES:
        return generate_theme_description(theme)

    if theme and random.random() < 0.7:
        return generate_theme_description(theme)

    return generate_category_description(category)


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


PREVIEW_FILENAME = "event_descriptions_preview.txt"
PREVIEW_RANDOM_SEED = 20260914


def build_description_preview():
    """Return a deterministic text preview without touching the database."""

    random_state = random.getstate()
    random.seed(PREVIEW_RANDOM_SEED)

    try:
        lines = [
            "EVENT HORIZON DESCRIPTION PREVIEW",
            "=" * 80,
            "",
            (
                "PREVIEW ONLY - no database records are created, updated, "
                "or deleted."
            ),
            (
                "Descriptions are generated with a fixed preview seed so the "
                "same code produces the same review text."
            ),
            "",
        ]

        current_category = None
        category_number = 0

        for event_data in EVENT_DATA:
            category = event_data["category"]

            if category != current_category:
                current_category = category
                category_number = 0

                if len(lines) > 6:
                    lines.append("")

                lines.extend([
                    category.upper(),
                    "=" * len(category),
                    "",
                ])

            category_number += 1
            description = generate_description(event_data)

            lines.extend([
                f"{category_number}. {event_data['name']}",
                "-" * 80,
                description,
                "",
            ])

        return "\n".join(lines).rstrip() + "\n"
    finally:
        random.setstate(random_state)



def build_description_update_plan():
    """Match the approved generated descriptions to existing event records."""

    random_state = random.getstate()
    random.seed(PREVIEW_RANDOM_SEED)

    try:
        update_plan = []
        missing_events = []
        duplicate_events = []

        for event_data in EVENT_DATA:
            category_name = event_data["category"]
            event_name = event_data["name"]
            description = generate_description(event_data)

            matching_events = Event.objects.filter(
                category__name=category_name,
                name=event_name,
            )
            match_count = matching_events.count()

            if match_count == 0:
                missing_events.append(
                    f"{category_name} / {event_name}"
                )
                continue

            if match_count > 1:
                duplicate_events.append(
                    f"{category_name} / {event_name} ({match_count} matches)"
                )
                continue

            event = matching_events.first()
            update_plan.append((event, description))

        if missing_events or duplicate_events:
            problems = []

            if missing_events:
                problems.append(
                    "Missing event records:\n- "
                    + "\n- ".join(missing_events)
                )

            if duplicate_events:
                problems.append(
                    "Duplicate event records:\n- "
                    + "\n- ".join(duplicate_events)
                )

            raise CommandError(
                "Description update cancelled before any database changes.\n\n"
                + "\n\n".join(problems)
            )

        return update_plan
    finally:
        random.setstate(random_state)


def update_existing_descriptions(dry_run=False):
    """Update only descriptions on the existing seeded event records."""

    update_plan = build_description_update_plan()
    changed_events = []
    unchanged_count = 0

    for event, description in update_plan:
        if event.description == description:
            unchanged_count += 1
            continue

        event.description = description
        changed_events.append(event)

    if dry_run:
        return {
            "matched": len(update_plan),
            "changed": len(changed_events),
            "unchanged": unchanged_count,
        }

    with transaction.atomic():
        if changed_events:
            Event.objects.bulk_update(
                changed_events,
                ["description"],
            )

    return {
        "matched": len(update_plan),
        "changed": len(changed_events),
        "unchanged": unchanged_count,
    }


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

        parser.add_argument(
            "--preview-descriptions",
            action="store_true",
            help=(
                "Write all generated event descriptions to a text file "
                "without changing the database."
            ),
        )

        parser.add_argument(
            "--update-descriptions",
            action="store_true",
            help=(
                "Update only the description field on matching existing "
                "event records."
            ),
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "With --update-descriptions, report what would change "
                "without writing to the database."
            ),
        )

    def handle(self, *args, **options):
        count = options["count"]
        clear = options["clear"]
        preview_descriptions = options["preview_descriptions"]
        update_descriptions = options["update_descriptions"]
        dry_run = options["dry_run"]

        if preview_descriptions and update_descriptions:
            raise CommandError(
                "Choose either --preview-descriptions or "
                "--update-descriptions, not both."
            )

        if dry_run and not update_descriptions:
            raise CommandError(
                "--dry-run can only be used with --update-descriptions."
            )

        if update_descriptions and clear:
            raise CommandError(
                "--clear cannot be combined with --update-descriptions."
            )

        if preview_descriptions:
            if clear:
                self.stdout.write(
                    self.style.WARNING(
                        "--clear is ignored while preview mode is active."
                    )
                )

            preview_path = Path(PREVIEW_FILENAME)
            preview_path.write_text(
                build_description_preview(),
                encoding="utf-8",
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "Description preview created without changing the "
                    f"database: {preview_path.resolve()}"
                )
            )
            return

        if update_descriptions:
            result = update_existing_descriptions(dry_run=dry_run)

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        "DRY RUN ONLY - no database records were changed."
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Matched {result['matched']} event(s): "
                        f"{result['changed']} would be updated, "
                        f"{result['unchanged']} already match the "
                        "approved descriptions."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated descriptions for {result['changed']} "
                        f"event(s). {result['unchanged']} event(s) already "
                        "matched. No other event fields were changed."
                    )
                )

            return

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
