"""Ep 128-148: the formula that worked best (aliens/mystery 1,023 views; 'one teaspoon weighs a billion tons' 541):
a personal question or an unbelievable claim in the first line, 45-60 s, one open debate question at the end."""
import json, os, re

OUT = "/home/claude/next-stop-universe/episodes"
DESC_TAIL = ("\n\nFollow for daily trips through the universe. 🚀\n\nImages: NASA, ESA, ESO and Wikimedia Commons "
             "(free licenses, credited in the video file's notes)\nNarration: AI voice\n\n")
BASE_TAGS = ["space", "universe", "astronomy", "space facts", "science shorts", "space mystery",
             "astronomy for beginners", "next stop universe"]


def I(text, headline=None, wiki=None, commons=None, query=None):
    v = {"type": "image", "query": query or (commons or [wiki or ""])[0] if isinstance(commons, list) else (query or commons or wiki)}
    if wiki: v["wiki"] = wiki if isinstance(wiki, list) else [wiki]
    if commons: v["commons"] = commons if isinstance(commons, list) else [commons]
    s = {"text": text, "visual": v}
    if headline: s["headline"] = headline
    return s


def C(text, big, label):
    return {"text": text, "visual": {"type": "card", "big": big, "label": label}}


def T(text, wiki=None, commons=None):
    v = {"type": "title", "query": (commons or [wiki])[0] if isinstance(commons, list) else (commons or wiki)}
    if wiki: v["wiki"] = wiki if isinstance(wiki, list) else [wiki]
    if commons: v["commons"] = commons if isinstance(commons, list) else [commons]
    return {"text": text, "visual": v}


def E(text, wiki=None, commons=None, warm=False):
    v = {"type": "end", "query": (commons or [wiki])[0] if isinstance(commons, list) else (commons or wiki), "warm": warm}
    v["wiki"] = ([wiki] if isinstance(wiki, str) else (wiki or []))
    v["commons"] = ([commons] if isinstance(commons, str) else (commons or []))
    return {"text": text, "visual": v}


EPS = []


def ep(n, slug, title, question, emoji, summary, tags, hashtags, segs):
    EPS.append(dict(n=n, slug=slug, title=title, question=question, emoji=emoji, summary=summary,
                    tags=tags, hashtags=hashtags, segs=segs))


ep(128, "are-aliens-watching-us", "The Zoo Hypothesis", "Are Aliens Watching You Right Now?", "👽",
   "Maybe the galaxy is full of life and they are quietly watching us, like visitors at a zoo. The zoo hypothesis, the 'dark forest' idea, and how far our own radio signals have travelled.",
   ["aliens", "zoo hypothesis", "dark forest", "fermi paradox", "seti", "are we alone"], "#aliens #space #fermiparadox",
   [T("What if aliens already know you exist, and they've decided not to say hello?", wiki="Milky Way", commons=["Milky Way night sky"]),
    I("Our radio and TV signals have been leaking into space for about a hundred years.", "We've been broadcasting", commons=["radio telescope night sky"], wiki="Arecibo Telescope"),
    C("That bubble of signals is now about a hundred light-years wide, and it holds thousands of stars.", "100", "light-years of our signals"),
    I("In nineteen seventy-three, an astronomer named John Ball suggested something unsettling: maybe they can hear us, and they're choosing to stay quiet.", "The zoo hypothesis", commons=["Earth from space night lights"]),
    I("Like visitors at a zoo, watching, but never stepping into the enclosure.", "Watching, not touching", wiki="Earth", commons=["The Earth seen from Apollo 17"]),
    I("Others have a darker idea: in a dangerous galaxy, the smart move is to hide. Some call it the dark forest.", "Or hiding?", commons=["Dark nebula stars"], wiki="Barnard 68"),
    C("Either way, the silence might not mean we're alone. It might mean we're being ignored.", "?", "alone, or ignored?"),
    E("So, would you want them to answer? Yes or no in the comments, and follow for the next stop.", wiki="Earthrise", commons=["Earthrise Apollo 8"])])

ep(129, "alien-signal-tonight", "First Contact", "What If We Heard an Alien Signal Tonight?", "📡",
   "What would actually happen if a radio telescope picked up an alien signal: checking it, announcing it, and why replying would take years.",
   ["alien signal", "first contact", "seti", "radio telescope", "aliens", "wow signal"], "#aliens #seti #space",
   [T("What would happen if scientists picked up an alien signal tonight?", wiki="Green Bank Telescope", commons=["Green Bank Telescope"]),
    I("First, nobody would celebrate. They'd try to prove it wrong.", "Step one: doubt it", commons=["radio telescope array night"], wiki="Very Large Array"),
    I("Is it a satellite? A phone? A microwave oven? That has fooled astronomers before.", "Is it us?", commons=["Parkes radio telescope"], wiki="Parkes Observatory"),
    I("Then a second telescope, on another continent, would have to hear the same thing.", "Check it twice", wiki="Allen Telescope Array"),
    C("SETI scientists agreed long ago: if it's real, tell the whole world. No secrets.", "1989", "SETI's first-contact rules"),
    C("But answering is a different story. Even the nearest star is over four light-years away. One hello and one reply would take nearly nine years.", "9 years", "for one hello and one reply"),
    I("And nobody has agreed who gets to speak for Earth.", "Who speaks for Earth?", wiki="Earth", commons=["The Earth seen from Apollo 17"]),
    E("If it were up to you, would we reply? Tell me in the comments, and follow for the next stop.", wiki="Milky Way", commons=["Milky Way night sky"])])

ep(130, "moon-spraying-ocean", "Enceladus", "There's a Moon Spraying Its Ocean Into Space", "🌊",
   "Saturn's moon Enceladus hides a salty ocean under its ice and blasts it into space through giant geysers. Cassini flew right through them and found the ingredients for life.",
   ["enceladus", "saturn moon", "geysers", "cassini", "ocean world", "life in space"], "#enceladus #saturn #space",
   [T("There's a moon out there spraying its own ocean into space.", wiki="Enceladus", commons=["PIA17202 - Approaching Enceladus"]),
    I("It's called Enceladus, a tiny white moon of Saturn, only about five hundred kilometers wide.", "Saturn's tiny moon", wiki="Enceladus"),
    I("Under its icy shell is a hidden ocean of salty water.", "An ocean under the ice", commons=["Enceladus interior ocean"], wiki="Enceladus"),
    I("And at its south pole, cracks in the ice blast that water out as giant geysers.", "Geysers into space", commons=["Enceladus plumes Cassini"]),
    I("So NASA did something wild. The Cassini spacecraft flew straight through the spray, and tasted it.", "Cassini tasted it", wiki="Cassini–Huygens"),
    C("It found salt, organic molecules, and in 2023, phosphorus. Ingredients life on Earth needs.", "Life's recipe?", "salt, organics, phosphorus"),
    I("Nobody has found life there. But it's one of the best places in the solar system to look.", "Is something living there?", commons=["Saturn rings Cassini"], wiki="Saturn"),
    E("Should we send a mission to look for life there? Yes or no in the comments, and follow for the next stop.", wiki="Saturn", commons=["Saturn global view from Cassini"])])

ep(131, "life-in-venus-clouds", "Life on Venus?", "Could Something Be Alive in the Clouds of Venus?", "☁️",
   "Venus's surface is hot enough to melt lead, but fifty kilometers up the clouds are surprisingly mild. In 2020 scientists reported a gas that might hint at life. The debate is still open.",
   ["venus", "phosphine", "life on venus", "venus clouds", "astrobiology", "aliens"], "#venus #space #aliens",
   [T("Could something be alive, floating in the clouds of Venus?", wiki="Venus", commons=["Venus Mariner 10 true color"]),
    C("On the ground, Venus is the hottest planet. Hot enough to melt lead.", "465°C", "on the surface of Venus"),
    I("But about fifty kilometers up, in the clouds, the temperature and pressure are a lot like Earth's.", "Mild, high in the clouds", wiki="Atmosphere of Venus", commons=["Venus clouds ultraviolet"]),
    I("In 2020, astronomers announced they'd spotted a gas there called phosphine. On Earth, it's mostly made by microbes.", "A strange gas", commons=["James Clerk Maxwell Telescope"], wiki="James Clerk Maxwell Telescope"),
    C("The news went around the world. Then other scientists checked, and many couldn't find it.", "?", "real signal, or a mistake?"),
    I("The debate is still going. New missions to Venus are being planned to settle it.", "Still unsolved", wiki="Venus", commons=["Venus - December 23 2016"]),
    E("Do you think something lives up there? Tell me in the comments, and follow for the next stop.", wiki="Venus", commons=["Venus from Mariner 10"], warm=True)])

ep(132, "sound-of-a-black-hole", "The Sound of a Black Hole", "What Does a Black Hole Sound Like?", "🔊",
   "Space is mostly silent, but in the Perseus galaxy cluster a black hole sends pressure waves through hot gas. NASA turned them into sound.",
   ["black hole sound", "perseus cluster", "nasa sonification", "chandra", "black hole", "sound in space"], "#blackhole #space #nasa",
   [T("You've heard that space is silent. But a black hole is humming, right now.", wiki="Perseus Cluster", commons=["Perseus galaxy cluster Chandra"]),
    I("It sits in a giant cluster of galaxies called Perseus, about two hundred and forty million light-years away.", "The Perseus cluster", wiki="Perseus Cluster"),
    I("The cluster is filled with hot gas. And gas can carry sound waves.", "Gas carries sound", commons=["Perseus cluster x-ray ripples"]),
    C("The black hole sends out ripples. Scientists measured the note: a B-flat, fifty-seven octaves below middle C.", "57", "octaves below middle C"),
    C("That's far too deep for any human ear, more than a quadrillion times too low.", "1 quadrillion×", "too low to hear"),
    I("So NASA sped it up until we could hear it. And it sounds like a haunted, rumbling moan.", "NASA made it audible", wiki="Chandra X-ray Observatory"),
    E("Search for it after this. Would you call it creepy or beautiful? Comment below, and follow for the next stop.", wiki="Black hole", commons=["Black hole - Messier 87 crop max res"])])

ep(133, "crying-in-space", "Tears in Space", "What Happens If You Cry in Space?", "😢",
   "Without gravity, tears don't fall. They gather into a wobbly ball of water on your eye, and they sting.",
   ["crying in space", "astronaut life", "microgravity", "iss", "chris hadfield", "space facts"], "#astronaut #space #iss",
   [T("What happens if you cry in space?", wiki="International Space Station", commons=["ISS-68 NASA astronaut Frank Rubio peers through a window in the cupola"]),
    I("On Earth, tears roll down your cheeks because gravity pulls them.", "Gravity pulls tears down", commons=["International Space Station over Earth"]),
    I("In orbit, everything is falling together, so your tears don't fall at all.", "Nothing falls", wiki="Weightlessness"),
    I("Instead, they pile up on your eye, forming a growing ball of water that clings to you.", "A ball of water on your eye", commons=["water bubble floating ISS astronaut"]),
    C("Astronauts say it stings. Chris Hadfield showed it on video in 2013, and it looks really uncomfortable.", "Ouch", "tears that won't fall"),
    I("The fix? Wipe it away with a towel, or shake your head and chase the tiny floating drops.", "Wipe it away", commons=["Astronaut Jessica Watkins is pictured eating a meal"]),
    E("Would you be able to handle living in space? Tell me in the comments, and follow for the next stop.", wiki="Earth", commons=["The Earth seen from Apollo 17"])])

ep(134, "venus-day-longer-than-year", "Venus Time", "Why Is a Day on Venus Longer Than Its Year?", "🌅",
   "Venus spins so slowly, and backwards, that one rotation takes longer than one trip around the Sun. On Venus the Sun rises in the west.",
   ["venus", "venus rotation", "day on venus", "retrograde rotation", "planets", "solar system"], "#venus #planets #space",
   [T("Imagine a world where your birthday comes around before the day ends.", wiki="Venus", commons=["Venus - December 23 2016"]),
    C("That's Venus. It takes two hundred and twenty-five Earth days to go around the Sun.", "225 days", "one year on Venus"),
    C("But it takes two hundred and forty-three days to spin around just once.", "243 days", "one spin of Venus"),
    I("So one turn of Venus is longer than its whole year.", "A day longer than a year", wiki="Venus", commons=["Venus Mariner 10 true color"]),
    I("And it spins backwards. If you stood on Venus, the Sun would rise in the west and set in the east.", "The Sun rises in the west", commons=["Maat Mons on Venus"]),
    C("Because it spins backwards, sunrise to sunrise takes about a hundred and seventeen Earth days.", "117 days", "from sunrise to sunrise"),
    E("How would you spend a sunrise that lasts for weeks? Tell me in the comments, and follow for the next stop.", wiki="Venus", commons=["Venus from Mariner 10"], warm=True)])

ep(135, "diamond-rain-neptune", "Diamond Rain", "Does It Really Rain Diamonds on Neptune?", "💎",
   "Deep inside Neptune and Uranus, crushing pressure may squeeze carbon into diamonds that sink like rain. In 2017 a lab experiment made tiny diamonds the same way.",
   ["diamond rain", "neptune", "uranus", "ice giants", "slac", "planets"], "#neptune #diamonds #space",
   [T("Deep inside Neptune, it might be raining diamonds.", wiki="Neptune", commons=["Neptune Voyager2 color calibrated"]),
    I("Neptune is a giant ball of gas and ice, far bigger than Earth.", "An ice giant", wiki="Neptune", commons=["Neptune Full"]),
    I("Its air contains methane, a gas made of carbon and hydrogen.", "Carbon in the air", commons=["Neptune clouds Voyager 2"]),
    C("Thousands of kilometers down, the pressure is millions of times higher than on Earth.", "Millions ×", "Earth's air pressure"),
    I("Scientists think that pressure squeezes the carbon out of methane, and packs it into diamonds.", "Squeezed into diamonds", commons=["diamond crystal macro"]),
    C("In 2017, a team in California blasted plastic with lasers to recreate those conditions. They made tiny diamonds.", "2017", "diamonds made in a lab"),
    I("So on Neptune and Uranus, diamonds may slowly sink toward the core, like hail.", "Diamond hail", wiki="Uranus", commons=["Uranus Voyager2 color calibrated"]),
    E("If you could bring back one Neptune diamond, what would you do with it? Comment below, and follow for the next stop.", wiki="Neptune", commons=["Neptune Full"])])

ep(136, "alcohol-cloud-in-space", "The Space Bar", "There's a Giant Cloud of Alcohol in Space", "🍹",
   "Near the center of our galaxy, the gas cloud Sagittarius B2 contains huge amounts of alcohol, and a molecule that smells like rum and raspberries.",
   ["sagittarius b2", "alcohol in space", "molecular cloud", "ethyl formate", "galactic center", "space facts"], "#space #galaxy #science",
   [T("Out in space, there's a cloud full of alcohol, bigger than our whole solar system.", wiki="Sagittarius B2", commons=["Center of the Milky Way Galaxy IV – Composite"]),
    I("It's called Sagittarius B2, a giant cloud of gas and dust near the center of our galaxy.", "Sagittarius B2", wiki="Sagittarius B2"),
    I("Radio telescopes found ethyl alcohol in it. The same kind that's in drinks.", "Real alcohol", commons=["ALMA and the centre of the Milky Way"], wiki="Atacama Large Millimeter Array"),
    C("And there's an unbelievable amount of it, far more than all the drinks ever made on Earth.", "Trillions", "of trillions of liters"),
    C("In 2009, astronomers also found ethyl formate there. On Earth, it gives raspberries their flavor, and it smells like rum.", "🍓", "smells like rum and raspberries"),
    I("But don't book a flight. It's about twenty-six thousand light-years away, and the alcohol is spread very, very thin.", "26,000 light-years away", commons=["ESO - Milky Way"], wiki="Galactic Center"),
    E("What would you name the bar at the center of the galaxy? Comment below, and follow for the next stop.", wiki="Milky Way", commons=["Milky Way night sky"])])

ep(137, "what-space-smells-like", "The Smell of Space", "What Does Space Smell Like?", "👃",
   "You can't breathe in space, but astronauts smell it on their suits and tools after spacewalks: burnt steak, hot metal, welding fumes.",
   ["smell of space", "spacewalk", "astronaut", "iss", "space facts", "eva"], "#astronaut #space #iss",
   [T("What does space smell like? Astronauts actually know.", wiki="Extravehicular activity", commons=["STS-116 spacewalk 1"]),
    I("You can't sniff space directly. Open your helmet and you'd be in serious trouble.", "Don't open the helmet", commons=["Ed White First American Spacewalker - GPN-2000-001180"]),
    I("But after a spacewalk, astronauts come back inside the airlock, and their suits and tools carry a smell.", "The smell comes inside", wiki="Quest Joint Airlock", commons=["ISS airlock spacewalk"]),
    C("They describe it as seared steak, hot metal, or welding fumes.", "🥩🔥", "seared steak and hot metal"),
    I("One idea: tiny bits of oxygen stuck to the suit react with the air inside, making that burnt smell.", "Why it smells", commons=["spacewalk astronaut Earth"]),
    I("Even the Moon has a smell. Apollo astronauts said Moon dust smelled like spent gunpowder.", "The Moon smells like gunpowder", commons=["A Man on the Moon, AS11-40-5903"], wiki="Lunar regolith"),
    E("Would you want to smell space for yourself? Tell me in the comments, and follow for the next stop.", wiki="Earth", commons=["The Earth seen from Apollo 17"])])

ep(138, "if-the-sun-disappeared", "No Sun", "What If the Sun Disappeared Right Now?", "☀️",
   "If the Sun vanished, you wouldn't notice for eight minutes. Then the sky goes dark, Earth flies off in a straight line, and the cold sets in.",
   ["sun disappeared", "what if", "sun", "eight minutes", "gravity", "space what if"], "#sun #whatif #space",
   [T("What if the Sun disappeared, right now?", wiki="Sun", commons=["The Sun by the Atmospheric Imaging Assembly of NASA's Solar Dynamics Observatory - 20100819"]),
    C("At first, nothing would happen. Sunlight takes about eight minutes to reach you.", "8 min 20 s", "for sunlight to reach Earth"),
    C("Gravity travels at the speed of light too, so for those eight minutes, Earth would keep circling an empty spot.", "8 minutes", "of not knowing"),
    I("Then, the sky goes black. The Moon and planets go dark too, because they only shine with sunlight.", "Darkness", commons=["Earth's City Lights by DMSP, 1994-1995"]),
    I("Earth would fly off in a straight line, into deep space.", "Earth flies away", wiki="Earth", commons=["The Earth seen from Apollo 17"]),
    C("Within about a week, temperatures would fall below freezing almost everywhere.", "Below 0°C", "within about a week"),
    I("But deep in the oceans, near hot volcanic vents, some life could keep going for a very long time.", "Life in the deep", commons=["hydrothermal vent black smoker"]),
    E("What would you do in your last eight minutes of sunlight? Comment below, and follow for the next stop.", wiki="Sun", commons=["Full disk of the Sun"], warm=True)])

ep(139, "if-earth-stopped-spinning", "Stop the Earth", "What If Earth Suddenly Stopped Spinning?", "🌍",
   "At the equator you are moving at about 1,670 km/h. If Earth stopped spinning, everything not attached to bedrock would keep going.",
   ["earth stopped spinning", "what if", "earth rotation", "planets", "physics", "space what if"], "#earth #whatif #space",
   [T("What would happen to you if Earth suddenly stopped spinning?", wiki="Earth", commons=["The Earth seen from Apollo 17"]),
    C("Right now, if you're near the equator, you're moving at about one thousand six hundred and seventy kilometers per hour.", "1,670 km/h", "your speed at the equator"),
    I("You don't feel it, because everything around you is moving too. The air, the oceans, the buildings.", "You don't feel it", commons=["Earth from space ISS"]),
    I("If the ground stopped, all of that would keep going. Winds faster than any hurricane would sweep the planet.", "Winds beyond any hurricane", commons=["ISS-20 Thunderstorms on the Brazilian Horizon"]),
    I("Oceans would surge across the land.", "Oceans on the move", commons=["ISS-45 StoryOfWater, Great Barrier Reef, Australia"]),
    C("And once things calmed down, one day would last a whole year: six months of daylight, then six months of night.", "6 months", "of daylight, then night"),
    I("Good news: Earth isn't going to stop. It's slowing, but only by milliseconds per century.", "Don't worry", wiki="Earth's rotation", commons=["Earthset"]),
    E("Would you rather live on the day side or the night side? Comment below, and follow for the next stop.", wiki="Earthrise", commons=["Earthrise Apollo 8"])])

ep(140, "18-minute-mystery-signal", "The 18-Minute Mystery", "What's Sending Signals Every 18 Minutes?", "📻",
   "In 2022 astronomers in Australia found an object that flashed radio waves every 18 minutes, for about a minute at a time. Nothing known behaved quite like it.",
   ["mystery signal", "gleam-x", "radio transient", "murchison widefield array", "space mystery", "magnetar"], "#spacemystery #space #astronomy",
   [T("Something in our galaxy was flashing radio waves at us, every eighteen minutes.", wiki="Murchison Widefield Array", commons=["Murchison Widefield Array"]),
    I("In 2022, astronomers in Australia were going through old data from a radio telescope in the desert.", "Hidden in old data", wiki="Murchison Widefield Array"),
    C("They found a source that switched on for about a minute, then off. Again and again.", "Every 18 min", "a minute-long flash"),
    C("It was about four thousand light-years away, and for a while it was one of the brightest radio sources in that part of the sky.", "4,000", "light-years away"),
    I("Pulsars flash too, but in seconds or less. Nobody had seen anything this slow.", "Too slow for a pulsar", commons=["Vela pulsar Chandra"], wiki="Pulsar"),
    I("It could be a strange kind of magnetar, or a white dwarf. Or something we haven't imagined.", "What is it?", commons=["magnetar artist impression"]),
    C("Since then, astronomers have found more of these slow flashers. And the mystery isn't fully solved.", "?", "still not fully explained"),
    E("What's your guess? Dead star, or something else? Comment below, and follow for the next stop.", wiki="Milky Way", commons=["ESO - Milky Way"])])

ep(141, "why-is-space-dark", "Why Is Space Dark?", "If There Are Trillions of Stars, Why Is the Night Sky Dark?", "🌌",
   "If the universe were endless and full of stars, every direction would end on a star and the night sky would blaze. It doesn't, because the universe has an age, and it is expanding.",
   ["olbers paradox", "why is space dark", "night sky", "big bang", "universe", "cosmology"], "#space #universe #science",
   [T("If there are trillions of stars, why is the night sky dark?", wiki="Hubble Ultra-Deep Field", commons=["Hubble ultra deep field high rez edit1"]),
    I("Think about it. If space went on forever, filled with stars, every direction you look would end on a star.", "Stars in every direction", commons=["Milky Way over Big Prairie"]),
    C("The whole sky would be as bright as the surface of the Sun. Day and night.", "☀️ everywhere", "a sky with no dark gaps"),
    I("This puzzle is called Olbers' paradox. The answer is hiding in the dark itself.", "Olbers' paradox", commons=["Guisard - Milky Way"]),
    C("The universe is about thirteen point eight billion years old. Light from stars farther away hasn't had time to reach us yet.", "13.8 billion", "years: not enough time"),
    I("And space is expanding, stretching old light until our eyes can't see it.", "Stretched light", wiki="Cosmic microwave background", commons=["Cosmic Microwave Background"]),
    I("So every time you see a dark night sky, you're seeing proof that the universe had a beginning.", "Proof of a beginning", commons=["A Dark Sky Full of Light"]),
    E("Did you ever wonder about this as a kid? Tell me in the comments, and follow for the next stop.", wiki="Milky Way", commons=["Milky Way night sky"])])

ep(142, "falling-from-space", "The Highest Jump", "Could You Survive Jumping From the Edge of Space?", "🪂",
   "In 2012 Felix Baumgartner jumped from about 39 km up and broke the speed of sound in free fall. In 2014 Alan Eustace jumped from over 41 km. Here is what that fall is really like.",
   ["space jump", "red bull stratos", "felix baumgartner", "alan eustace", "free fall", "stratosphere"], "#spacejump #space #science",
   [T("Could you jump from the edge of space, and survive?", commons=["stratosphere earth curvature balloon"], wiki="Stratosphere"),
    C("In 2012, a skydiver rode a balloon up to about thirty-nine kilometers, more than three times higher than a passenger jet.", "39 km", "up, in a balloon"),
    I("The air up there is so thin that your blood would boil without a pressure suit.", "You need a pressure suit", commons=["pressure suit stratosphere"]),
    C("He stepped off, and with almost no air to slow him down, he fell faster than the speed of sound.", "1,357 km/h", "in free fall"),
    I("He went into a dangerous spin, but got control, and opened his parachute safely.", "A deadly spin", commons=["parachute sky"]),
    C("Two years later, a Google executive named Alan Eustace jumped from over forty-one kilometers.", "41 km", "the record"),
    I("But real space starts at about a hundred kilometers. From orbit, you'd be moving sideways too fast to just fall. You'd need a heat shield.", "Space is higher", wiki="Kármán line", commons=["Moon over Horizon - ISS - August 30 2026"]),
    E("Would you ever do this jump? Yes or no in the comments, and follow for the next stop.", wiki="Earth", commons=["The Earth seen from Apollo 17"])])

ep(143, "hotter-than-a-star", "KELT-9b", "This Planet Is Hotter Than Most Stars", "🔥",
   "KELT-9b orbits so close to its star that its day side reaches about 4,300 °C, hotter than most stars in our galaxy. A year there lasts a day and a half.",
   ["kelt-9b", "hottest planet", "ultra hot jupiter", "exoplanet", "planets", "space facts"], "#exoplanet #space #astronomy",
   [T("Imagine a planet so hot, it's hotter than most stars.", wiki="KELT-9b", commons=["Artist’s impression of an ultra-hot Jupiter transiting its star"]),
    I("It's called KELT-9b, a giant planet bigger than Jupiter, discovered in 2017.", "KELT-9b", wiki="KELT-9b"),
    C("It orbits so close to its star that a whole year there takes just a day and a half.", "1.5 days", "one year on KELT-9b"),
    C("The side facing its star reaches about four thousand three hundred degrees Celsius.", "4,300°C", "on the day side"),
    I("That's hotter than most stars in our galaxy, which are cooler red dwarfs.", "Hotter than most stars", commons=["red dwarf star artist impression"]),
    I("It's so hot that metals like iron and titanium float in its air as vapor.", "Iron in the air", commons=["Artist Impression of the exoplanet WASP-76b"]),
    I("And its star is slowly boiling its atmosphere away into space.", "Boiling away", commons=["Artist's concept of exoplanet with comet-like tail"]),
    E("Hottest planet or coldest planet, which would you visit for one second? Comment below, and follow for the next stop.", wiki="Sun", commons=["Full disk of the Sun"], warm=True)])

ep(144, "glass-rain-planet", "HD 189733b", "The Blue Planet Where It Rains Glass Sideways", "🌧️",
   "HD 189733b looks like a deep blue marble, but its winds blow at thousands of km/h and may carry silicate particles: glass, flying sideways.",
   ["hd 189733b", "glass rain", "exoplanet", "hot jupiter", "weird planets", "james webb"], "#exoplanet #space #weirdplanets",
   [T("There's a beautiful blue planet out there. But you'd never want to stand in its rain.", wiki="HD 189733 b", commons=["HD 189733b artist impression"]),
    I("It's called HD 189733b, about sixty-four light-years from us.", "64 light-years away", wiki="HD 189733 b"),
    I("From far away it looks deep blue, like Earth. But it's a gas giant, roasting close to its star.", "Blue, but deadly", commons=["blue exoplanet artist impression"]),
    C("Winds there blow at about eight thousand seven hundred kilometers per hour.", "8,700 km/h", "winds"),
    I("Scientists think its clouds hold tiny bits of silicate, the stuff glass is made of.", "Clouds of glass", commons=["glass shards"]),
    C("So the rain might be glass, flying sideways at seven times the speed of sound.", "Glass", "rain, sideways"),
    I("And in 2024, the Webb telescope found it smells like rotten eggs.", "It stinks too", wiki="James Webb Space Telescope", commons=["James Webb Space Telescope Artist Conception"]),
    E("Worst weather in the galaxy? Name a worse one in the comments, and follow for the next stop.", wiki="Neptune", commons=["Neptune Full"])])

ep(145, "tv-static-big-bang", "Echo of the Big Bang", "Did You Know Old TV Static Showed the Big Bang?", "📺",
   "A small part of the static on old analog TVs came from the cosmic microwave background, light released 380,000 years after the Big Bang. It was discovered by accident in 1965.",
   ["cosmic microwave background", "big bang", "tv static", "penzias and wilson", "cmb", "cosmology"], "#bigbang #space #science",
   [T("If you ever saw static on an old TV, you saw a little bit of the Big Bang.", wiki="Cosmic microwave background", commons=["Cosmic Microwave Background"]),
    I("When an old TV couldn't find a channel, it showed snowy static.", "TV snow", commons=["television static noise"]),
    C("About one percent of that static was a signal from the beginning of the universe.", "~1%", "of the static"),
    I("It's called the cosmic microwave background. Light released about three hundred and eighty thousand years after the Big Bang.", "The oldest light", wiki="Cosmic microwave background"),
    C("It has been travelling for thirteen point eight billion years to reach you.", "13.8 billion", "years old"),
    I("It was found by accident in 1965. Two radio engineers kept hearing a hiss in their antenna. They even cleaned out pigeon droppings to get rid of it.", "Blame the pigeons?", wiki="Holmdel Horn Antenna"),
    C("The hiss didn't go away. It was the Big Bang. They won a Nobel Prize for it.", "Nobel", "Prize, 1978"),
    E("Do you remember TV static? Tell me how old you are in the comments, and follow for the next stop.", wiki="Hubble Ultra-Deep Field", commons=["Hubble ultra deep field"])])

ep(146, "earth-as-black-hole", "A Pocket Black Hole", "What If Earth Became a Black Hole?", "🕳️",
   "To turn Earth into a black hole you would have to crush it down to about 2 centimeters across, the size of a marble. And the Moon would keep orbiting it.",
   ["black hole", "schwarzschild radius", "earth black hole", "what if", "physics", "gravity"], "#blackhole #whatif #space",
   [T("If Earth turned into a black hole, you could hold it in your hand.", wiki="Black hole", commons=["Artist's impression of a black hole and accretion disk"]),
    I("Any object can become a black hole, if you squeeze it small enough.", "Squeeze it small", commons=["Black hole - Messier 87 crop max res"]),
    C("For Earth, all six sextillion tonnes would have to fit into a ball about eighteen millimeters wide.", "18 mm", "Earth as a black hole"),
    C("That's the size of a marble.", "🔮", "the size of a marble"),
    I("Here's the weird part: the Moon wouldn't fall in. It would keep orbiting, because Earth's mass, and its pull, would be the same.", "The Moon keeps orbiting", commons=["Earth-Moon-edit3"], wiki="Moon"),
    C("The Sun would need to shrink to about six kilometers across. Smaller than a city.", "6 km", "the Sun as a black hole"),
    I("Luckily, neither of them is heavy enough to ever collapse like that on their own.", "Don't panic", wiki="Earth", commons=["The Earth seen from Apollo 17"]),
    E("Would you hold a marble-sized black hole? Just kidding. Don't. Tell me what you'd do in the comments, and follow for the next stop.", wiki="Black hole", commons=["Black hole - Messier 87 crop max res"])])

ep(147, "supernova-in-daylight", "SN 1006", "What If a Star Exploded So Bright You Could See It in Daylight?", "💥",
   "In the year 1006, a supernova appeared that was bright enough to see during the day and to read by at night. People recorded it in China, Japan, Egypt and Europe.",
   ["sn 1006", "supernova", "brightest supernova", "history of astronomy", "betelgeuse", "exploding star"], "#supernova #space #history",
   [T("A thousand years ago, a star exploded so brightly, people could see it in broad daylight.", wiki="SN 1006", commons=["SN 1006 Chandra"]),
    C("It happened in the year one thousand and six. A new star suddenly appeared in the southern sky.", "1006", "a new star appears"),
    C("It was the brightest star-like event in recorded history, far brighter than Venus.", "Brightest", "ever recorded"),
    I("Some reports say it was bright enough to read by at night. And it stayed visible for months.", "Visible for months", commons=["Kepler's supernova"], wiki="Kepler's Supernova"),
    I("People wrote about it in China, Japan, Egypt and Europe. A doctor in Cairo said it was three times bigger than Venus.", "Seen around the world", commons=["Night sky ancient observatory"]),
    C("It was a white dwarf star that exploded about seven thousand light-years away.", "7,200", "light-years away"),
    I("Today, telescopes can still see the expanding cloud it left behind.", "Still expanding", wiki="SN 1006"),
    E("If a star exploded in daylight tomorrow, what would you think was happening? Comment below, and follow for the next stop.", wiki="Crab Nebula", commons=["Crab Nebula"])])

ep(148, "hole-in-the-sky", "Barnard 68", "Why Is There a Hole in the Sky?", "⚫",
   "Barnard 68 looks like a hole punched in the sky, but it is a cold, dark cloud of dust and gas about 500 light-years away, blocking the stars behind it. One day it may form new stars.",
   ["barnard 68", "dark nebula", "molecular cloud", "star formation", "eso", "space mystery"], "#space #nebula #astronomy",
   [T("Astronomers found what looks like a hole in the sky, where the stars just disappear.", wiki="Barnard 68", commons=["Barnard 68"]),
    I("It's called Barnard 68. Look at it. Thousands of stars, and then nothing.", "A hole in the stars?", wiki="Barnard 68"),
    I("It's not empty space, and it's not a black hole. It's a cloud of cold dust and gas, blocking the stars behind it.", "A cloud, not a hole", commons=["dark nebula stars"]),
    C("It's about half a light-year wide and five hundred light-years away.", "500", "light-years away"),
    C("Inside, it's one of the coldest places nearby. Just a few degrees above absolute zero.", "−257°C", "inside the cloud"),
    I("With infrared cameras, astronomers can see straight through it, to the stars behind.", "Seeing through it", commons=["Barnard 68 infrared"]),
    I("And one day, gravity may squeeze it so hard that it collapses, and a brand new star switches on.", "A future star", commons=["Eagle Nebula from ESO"], wiki="Pillars of Creation"),
    E("Did it look like a black hole to you at first? Tell me in the comments, and follow for the next stop.", wiki="Milky Way", commons=["Guisard - Milky Way"])])


def build():
    out = []
    for e in EPS:
        n = e["n"]
        words = sum(len(s["text"].split()) for s in e["segs"])
        d = {
            "number": n,
            "title": e["title"],
            "subtitle": e["question"],
            "next_stop": "",
            "yt_title": f"{e['question']} {e['emoji']} #shorts",
            "description": f"{e['question']}\n\n{e['summary']}{DESC_TAIL}{e['hashtags']} #astronomy #shorts #science",
            "tags": e["tags"] + [t for t in BASE_TAGS if t not in e["tags"]],
            "segments": e["segs"],
        }
        p = os.path.join(OUT, f"ep{n:03d}-{e['slug']}.json")
        json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
        out.append((n, words, len(d["yt_title"])))
    return out


if __name__ == "__main__":
    for r in build():
        print(r)
