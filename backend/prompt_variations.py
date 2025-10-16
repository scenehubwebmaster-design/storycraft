"""
Enhanced Character Generation Prompts with Genre Variations
Provides 10+ high-quality prompt variations across Fantasy, Sci-Fi, and Historical genres
"""

# ============================================================================
# FANTASY CHARACTER PROMPTS (10 Variations)
# ============================================================================

FANTASY_VARIATIONS = {
    "high_fantasy": {
        "name": "High Fantasy (Epic Adventure)",
        "description": "Classic fantasy with heroes, magic, and epic quests",
        "prompt_additions": """
FANTASY SETTING: High Fantasy (Epic Adventure)
- World: Medieval-inspired realm with ancient magic and legendary heroes
- Magic Level: Abundant and powerful, woven into daily life
- Conflict: Epic good vs evil, world-threatening dangers
- Tone: Heroic, inspiring, adventure-filled

CHARACTER FOCUS:
- Consider heroic archetypes: chosen ones, noble knights, wise wizards
- Magic abilities or connections to ancient powers
- Ties to legendary bloodlines, artifacts, or prophecies
- Clear moral compass (good, evil, or redemption arc)
- Potential for epic quests and world-saving adventures
- Relationships with other races (elves, dwarves, etc.)

SPECIFIC DETAILS TO INCLUDE:
- Magical abilities or potential (specify school/type of magic)
- Connection to prophecies or ancient lore
- Relationship with magical creatures or beings
- Equipment: legendary weapons, magical items, artifacts
- Noble title or common origin with destiny
""",
    },
    
    "dark_fantasy": {
        "name": "Dark Fantasy (Gritty & Morally Grey)",
        "description": "Grim fantasy with moral complexity and harsh realities",
        "prompt_additions": """
FANTASY SETTING: Dark Fantasy (Gritty & Morally Grey)
- World: Harsh, unforgiving realm where survival is paramount
- Magic Level: Dangerous, corrupting, with terrible costs
- Conflict: Morally ambiguous struggles, no clear heroes
- Tone: Grim, mature, psychologically complex

CHARACTER FOCUS:
- Flawed, complex motivations (survival, revenge, desperation)
- Traumatic past events and psychological scars
- Moral grey areas: questionable choices, necessary evils
- Internal conflicts between ideals and reality
- Survival skills and street smarts
- Potential for corruption or redemption

SPECIFIC DETAILS TO INCLUDE:
- Dark secrets or guilt they carry
- Costs they've paid for power or survival
- Scars (physical and psychological) and their origins
- Morally questionable skills or methods
- Relationships damaged or lost due to their choices
- What lines they will/won't cross and why
""",
    },
    
    "urban_fantasy": {
        "name": "Urban Fantasy (Magic in Modern World)",
        "description": "Contemporary setting with hidden magical elements",
        "prompt_additions": """
FANTASY SETTING: Urban Fantasy (Magic in Modern World)
- World: Modern city with supernatural hidden beneath surface
- Magic Level: Secret from mundane world, carefully concealed
- Conflict: Balance between magical and mundane, secret wars
- Tone: Contemporary with mystical undertones, dual identities

CHARACTER FOCUS:
- Double life: mundane job/social life + magical identity
- Modern skills combined with supernatural abilities
- Connections to hidden magical communities or organizations
- Struggle to maintain the masquerade/veil
- Contemporary problems amplified by magical complications
- Tech-savvy with magical knowledge

SPECIFIC DETAILS TO INCLUDE:
- Day job or cover identity in modern world
- How they discovered/inherited their powers
- Relationship with both mundane and magical communities
- Modern possessions: phone, apartment, car, etc.
- Magical organizations they're affiliated with (or hiding from)
- How they balance normal life with supernatural obligations
- Contemporary clothing style with subtle magical elements
""",
    },
    
    "cozy_fantasy": {
        "name": "Cozy Fantasy (Low-Stakes & Wholesome)",
        "description": "Gentle fantasy focused on community and everyday magic",
        "prompt_additions": """
FANTASY SETTING: Cozy Fantasy (Low-Stakes & Wholesome)
- World: Warm, inviting fantasy realm focused on community
- Magic Level: Gentle, helpful, part of everyday life
- Conflict: Personal growth, small community challenges
- Tone: Wholesome, comforting, slice-of-life

CHARACTER FOCUS:
- Relatable everyday concerns and aspirations
- Focus on community, friendships, and belonging
- Cozy profession: baker, innkeeper, librarian, gardener
- Small but meaningful personal goals
- Kind-hearted with gentle flaws
- Growth through connection and self-discovery

SPECIFIC DETAILS TO INCLUDE:
- Cozy profession or craft they practice
- Favorite comfort activities (baking, reading, gardening)
- Close friendships and found family
- Small daily rituals and routines
- Comfort items: favorite tea, cozy sweater, beloved book
- What makes them feel safe and happy
- Community role and how they help others
- Magical abilities that aid daily life (not combat)
""",
    },
    
    "sword_and_sorcery": {
        "name": "Sword & Sorcery (Pulp Adventure)",
        "description": "Action-focused fantasy with rogues and mercenaries",
        "prompt_additions": """
FANTASY SETTING: Sword & Sorcery (Pulp Adventure)
- World: Exotic, dangerous lands filled with treasure and peril
- Magic Level: Mysterious, ancient, often dangerous to wield
- Conflict: Personal survival, fortune-seeking, revenge
- Tone: Action-packed, adventurous, morally flexible

CHARACTER FOCUS:
- Skilled warrior, cunning rogue, or opportunistic mercenary
- Motivated by personal gain, revenge, or survival
- Pragmatic and adaptable to dangerous situations
- Combat prowess and street smarts
- Relationships based on mutual benefit or past debts
- Anti-hero qualities with personal code of honor

SPECIFIC DETAILS TO INCLUDE:
- Combat style and signature weapons
- Notable fights or victories
- Scars and how they got them
- Current job: mercenary, treasure hunter, assassin, bodyguard
- Personal code of honor (what rules they follow)
- Debts owed or grudges held
- Exotic places they've traveled
- Preferred fighting techniques and dirty tricks
""",
    },
    
    "mythological_fantasy": {
        "name": "Mythological Fantasy (Gods & Legends)",
        "description": "Fantasy inspired by real-world mythology and legends",
        "prompt_additions": """
FANTASY SETTING: Mythological Fantasy (Gods & Legends)
- World: Realm where gods walk among mortals, mythology is real
- Magic Level: Divine power, ancient and absolute
- Conflict: Between gods and mortals, fate vs free will
- Tone: Epic, timeless, larger-than-life

CHARACTER FOCUS:
- Connection to specific mythology (Greek, Norse, Egyptian, Celtic, Asian, etc.)
- Relationship with gods, divine bloodline, or chosen status
- Heroic journey echoing classical myths
- Struggle with fate, prophecy, or divine will
- Classical virtues and tragic flaws
- Legacy and legend-building

SPECIFIC DETAILS TO INCLUDE:
- Specific mythological tradition they're tied to
- Divine parentage, blessing, or curse
- Prophesied destiny or fated path
- Classical heroic virtues (courage, wisdom, honor)
- Tragic flaw or hubris
- Sacred items or divine gifts
- Relationship with specific deities
- Classical trials or quests they've undertaken
- How mortals might speak of them in legend
""",
    },
    
    "steampunk_fantasy": {
        "name": "Steampunk Fantasy (Magical Victorian Tech)",
        "description": "Victorian-era aesthetics with magic-powered technology",
        "prompt_additions": """
FANTASY SETTING: Steampunk Fantasy (Magical Victorian Tech)
- World: Victorian-inspired with brass, steam, and magic-tech fusion
- Magic Level: Industrialized, combined with machinery
- Conflict: Class struggles, industrial revolution, innovation vs tradition
- Tone: Inventive, elegant, industrial

CHARACTER FOCUS:
- Inventor, engineer, airship pilot, or magical technician
- Victorian-era profession with steampunk twist
- Understanding of both magic and mechanics
- Class consciousness (aristocrat, working class, or rising middle)
- Progressive thinking or tradition-bound
- Relationship with automatons, airships, or magical devices

SPECIFIC DETAILS TO INCLUDE:
- Specific steampunk profession or expertise
- Inventions or devices they've created/operate
- Victorian-era clothing with steampunk modifications
- Goggle type, pocket watch, mechanical limbs, etc.
- Social class and how it affects their opportunities
- Stance on industrial magic vs traditional magic
- Airship or workshop they frequent
- Favorite gadgets and tools
- How they blend magic with technology
""",
    },
    
    "fairy_tale_fantasy": {
        "name": "Fairy Tale Fantasy (Enchanted & Whimsical)",
        "description": "Storybook fantasy with enchantments and wonder",
        "prompt_additions": """
FANTASY SETTING: Fairy Tale Fantasy (Enchanted & Whimsical)
- World: Enchanted realm where stories and magic intertwine
- Magic Level: Whimsical, wish-granting, transformative
- Conflict: Curses to break, true love, self-discovery
- Tone: Whimsical, magical, with deeper wisdom

CHARACTER FOCUS:
- Fairy tale archetype with a twist or subversion
- Magical transformation or curse affecting them
- Quest for true love, identity, or breaking free
- Connection to enchanted forests, towers, or castles
- Animal companions or magical helpers
- Lesson to learn or wisdom to gain

SPECIFIC DETAILS TO INCLUDE:
- Fairy tale role (princess, woodcutter, witch, knight, etc.)
- Magical curse, blessing, or transformation
- Enchanted item they possess
- Animal companion or magical ally
- What they wish for most deeply
- Traditional fairy tale lesson applied to their life
- Enchanted location they're connected to
- How they subvert or fulfill their archetype
""",
    },
    
    "post_apocalyptic_fantasy": {
        "name": "Post-Apocalyptic Fantasy (Magic After the Fall)",
        "description": "Fantasy in a world recovering from magical catastrophe",
        "prompt_additions": """
FANTASY SETTING: Post-Apocalyptic Fantasy (Magic After the Fall)
- World: Ruins of once-great magical civilization
- Magic Level: Unpredictable, dangerous, remnants of old power
- Conflict: Survival, rebuilding, understanding lost knowledge
- Tone: Harsh but hopeful, archaeological mystery

CHARACTER FOCUS:
- Survivor with adaptation and resourcefulness
- Relationship to old world (memory, ruins, artifacts)
- Scavenging skills and magical salvage knowledge
- Hope for rebuilding or acceptance of new reality
- Lost magical knowledge they seek to recover
- Mutations or changes caused by magical catastrophe

SPECIFIC DETAILS TO INCLUDE:
- What they remember of the world before (if anything)
- Survival skills in magical wasteland
- Scavenged magical items or pre-fall artifacts
- Mutations or magical alterations they've developed
- Ruins they explore or avoid
- Knowledge of old magic they've pieced together
- How they survive day-to-day
- Hope or cynicism about the future
- Faction or settlement they belong to
""",
    },
    
    "portal_fantasy": {
        "name": "Portal Fantasy (Outsider in Magic World)",
        "description": "Character from our world discovering magical realm",
        "prompt_additions": """
FANTASY SETTING: Portal Fantasy (Outsider in Magic World)
- World: Magical realm accessed from mundane Earth
- Magic Level: New and wondrous to the protagonist
- Conflict: Adapting to magic, finding purpose, returning home?
- Tone: Fish-out-of-water, wonder and discovery

CHARACTER FOCUS:
- Modern person thrust into fantasy setting
- Initial skepticism giving way to wonder
- Modern knowledge applied to magical problems
- Struggle to adapt to new rules and customs
- Questioning whether to return home or stay
- Unique perspective as an outsider

SPECIFIC DETAILS TO INCLUDE:
- Life in normal world before portal (school, job, family)
- How they discovered/fell through the portal
- Modern items they brought with them
- Modern knowledge useful in fantasy world (science, pop culture)
- Culture shock moments and misunderstandings
- What they miss from home
- What draws them to stay in magical world
- How their modern perspective changes fantasy world
- Whether they can return home and if they want to
""",
    },
}

# ============================================================================
# SCI-FI CHARACTER PROMPTS (10 Variations)
# ============================================================================

SCI_FI_VARIATIONS = {
    "space_opera": {
        "name": "Space Opera (Galactic Adventure)",
        "description": "Epic space adventures across star systems",
        "prompt_additions": """
SCI-FI SETTING: Space Opera (Galactic Adventure)
- World: Vast galaxy with multiple alien species and civilizations
- Technology Level: FTL travel, energy weapons, advanced AI
- Conflict: Galactic politics, space wars, exploration
- Tone: Epic, adventurous, larger-than-life

CHARACTER FOCUS:
- Starship pilot, smuggler, rebel, or space navy officer
- Experience with multiple alien cultures
- FTL travel experience and space combat skills
- Political intrigue and factional allegiances
- Romantic, swashbuckling heroics
- Destiny tied to galactic events

SPECIFIC DETAILS TO INCLUDE:
- Starship they pilot or serve on (name, class, condition)
- Alien species they've encountered and relationships
- Space combat or piloting skills
- Faction allegiance (empire, rebellion, independent)
- Exotic planets they've visited
- Signature weapon or tool (blaster, energy sword, etc.)
- Rank or reputation in space-faring community
- Personal ship modifications or prized possessions
- Notable battles or adventures
""",
    },
    
    "cyberpunk": {
        "name": "Cyberpunk (High Tech, Low Life)",
        "description": "Dystopian future with advanced technology and corporate control",
        "prompt_additions": """
SCI-FI SETTING: Cyberpunk (High Tech, Low Life)
- World: Mega-cities controlled by corporations, tech-augmented humans
- Technology Level: Neural implants, AI, virtual reality, body mods
- Conflict: Corporate oppression, transhumanism, identity
- Tone: Dark, gritty, neon-soaked, rebellious

CHARACTER FOCUS:
- Hacker, street samurai, corpo, or netrunner
- Cybernetic enhancements and their consequences
- Anti-corporate sentiment or corporate allegiance
- Digital and physical skills
- Identity in age of body modification
- Underground connections and street cred

SPECIFIC DETAILS TO INCLUDE:
- Cybernetic augmentations (neural jacks, cyber-eyes, enhanced reflexes, etc.)
- Hacking skills and favorite programs/viruses
- Corporate affiliation or enemies
- Street name/handle in hacker community
- Favorite dive bars or underground clubs
- Virtual reality addiction or habits
- Debts to fixers or crime syndicates
- Black market connections
- What parts of their humanity they've traded for chrome
- Signature style (leather, neon, tactical)
""",
    },
    
    "hard_sci_fi": {
        "name": "Hard Science Fiction (Realistic Future)",
        "description": "Scientifically accurate near-future or realistic space setting",
        "prompt_additions": """
SCI-FI SETTING: Hard Science Fiction (Realistic Future)
- World: Near-future Earth or realistic space colonization
- Technology Level: Extrapolated from current science, no FTL
- Conflict: Resource scarcity, survival, scientific challenges
- Tone: Cerebral, realistic, problem-solving focused

CHARACTER FOCUS:
- Scientist, engineer, astronaut, or colonist
- Expertise in specific scientific field
- Practical problem-solving skills
- Psychological resilience in harsh conditions
- Understanding of realistic space/science limitations
- Education and research background

SPECIFIC DETAILS TO INCLUDE:
- Specific scientific or engineering expertise
- Educational background (degrees, institutions)
- Research or mission they're part of
- Realistic technology they work with
- Space station, colony, or research facility
- Scientific papers or discoveries
- Practical survival skills
- Psychological training or therapy
- What they miss about Earth (if off-world)
- Realistic challenges they face (radiation, isolation, resources)
""",
    },
    
    "post_apocalyptic_sci_fi": {
        "name": "Post-Apocalyptic Sci-Fi (After the Fall)",
        "description": "Surviving in the ruins of technological civilization",
        "prompt_additions": """
SCI-FI SETTING: Post-Apocalyptic Sci-Fi (After the Fall)
- World: Earth after nuclear war, plague, or ecological collapse
- Technology Level: Scavenged pre-war tech, primitive rebuilding
- Conflict: Survival, resource wars, rebuilding society
- Tone: Harsh, survivalist, desperate hope

CHARACTER FOCUS:
- Wasteland survivor, scavenger, or vault dweller
- Adaptation to harsh new world
- Scavenging and repair skills
- Memories of old world or born in wasteland
- Moral choices in lawless world
- Building community or lone wolf

SPECIFIC DETAILS TO INCLUDE:
- How they survived the apocalypse (vault, bunker, luck)
- Scavenging expertise (what they can find and fix)
- Weapons cobbled from pre-war tech
- Radiation sickness, mutations, or adaptations
- Pre-war relics they treasure
- Faction or settlement allegiance
- Survival skills (water purification, hunting, defense)
- What they remember or heard about the old world
- Hope or cynicism about humanity's future
""",
    },
    
    "first_contact": {
        "name": "First Contact (Meeting Alien Life)",
        "description": "Humanity's first encounter with extraterrestrial intelligence",
        "prompt_additions": """
SCI-FI SETTING: First Contact (Meeting Alien Life)
- World: Contemporary or near-future Earth during first contact
- Technology Level: Human tech meeting advanced alien tech
- Conflict: Communication barriers, cultural exchange, fear
- Tone: Wondrous, tense, diplomatic

CHARACTER FOCUS:
- Linguist, diplomat, scientist, or military first responder
- Adaptability and open-mindedness
- Scientific curiosity and cultural sensitivity
- Handling fear of the unknown
- Historic significance of their role
- Bridge between species or protector of humanity

SPECIFIC DETAILS TO INCLUDE:
- Expertise relevant to contact (linguistics, xenobiology, diplomacy)
- Initial reaction to alien life
- Communication attempts and breakthroughs
- Cultural assumptions challenged
- Fear vs curiosity balance
- Protocol or orders from government
- Personal philosophy on humanity's place in cosmos
- Relationship with specific aliens
- Historic moment awareness
- What first contact means to them personally
""",
    },
    
    "time_travel": {
        "name": "Time Travel (Temporal Adventures)",
        "description": "Adventures through time, changing or preserving history",
        "prompt_additions": """
SCI-FI SETTING: Time Travel (Temporal Adventures)
- World: Multiple time periods accessible via technology or anomaly
- Technology Level: Varies by era visited, time machine technology
- Conflict: Paradoxes, timeline preservation, temporal wars
- Tone: Mind-bending, adventurous, philosophical

CHARACTER FOCUS:
- Time traveler (by choice, accident, or profession)
- Knowledge of history from multiple eras
- Understanding of butterfly effect and paradoxes
- Adaptability to different time periods
- Burden of temporal knowledge
- Mission or personal reason for traveling

SPECIFIC DETAILS TO INCLUDE:
- How they gained access to time travel
- Favorite time period to visit and why
- Temporal paradoxes they've encountered
- Historical events they've witnessed
- Objects from different eras they carry
- Knowledge of "future" technology or events
- Temporal organization they work for (or rebel against)
- Personal timeline complications
- What era they originally came from
- Rules of time travel they follow (or break)
""",
    },
    
    "military_sci_fi": {
        "name": "Military Science Fiction (Soldiers of the Future)",
        "description": "Military operations with advanced technology and alien threats",
        "prompt_additions": """
SCI-FI SETTING: Military Science Fiction (Soldiers of the Future)
- World: Interstellar military conflict, alien wars, space marines
- Technology Level: Power armor, plasma weapons, tactical AI
- Conflict: War against aliens, human factions, or AI
- Tone: Action-packed, tactical, brotherhood-focused

CHARACTER FOCUS:
- Soldier, officer, or specialist in futuristic military
- Combat experience and tactical expertise
- Unit loyalty and military brotherhood
- PTSD or psychological impacts of war
- Following orders vs moral choices
- Military rank and reputation

SPECIFIC DETAILS TO INCLUDE:
- Military branch and rank
- Specialized training (drop trooper, sniper, medic, pilot)
- Power armor or advanced equipment
- Combat decorations and commendations
- Unit history and notable battles
- Comrades lost and how it affects them
- Combat tactics and signature moves
- Relationship with chain of command
- Alien enemies faced
- What they're fighting for (duty, survival, belief)
""",
    },
    
    "biopunk": {
        "name": "Biopunk (Biological Engineering)",
        "description": "World transformed by genetic engineering and biotech",
        "prompt_additions": """
SCI-FI SETTING: Biopunk (Biological Engineering)
- World: Society reshaped by genetic engineering and biotechnology
- Technology Level: Gene-mods, bio-augmentation, engineered organisms
- Conflict: Designer babies, bio-warfare, identity and humanity
- Tone: Body-horror adjacent, ethical questions, visceral

CHARACTER FOCUS:
- Genetic engineer, bio-modded human, or bio-hacker
- Genetically engineered traits or modifications
- Ethical stance on genetic modification
- Relationship with un-modded "naturals"
- Bio-augmentations and their side effects
- Creation or rejection of engineered life

SPECIFIC DETAILS TO INCLUDE:
- Genetic modifications (enhanced traits, cosmetic changes, abilities)
- Bio-augmentations (living implants, symbiotes, engineered organs)
- Expertise in genetics or biotechnology
- Designer genes vs natural birth
- Side effects or complications of modifications
- Ethical line they won't cross
- Lab or bio-corporation affiliation
- Engineered creatures they work with
- What their gene-profile says about their "design"
- Natural vs artificial identity struggle
""",
    },
    
    "solar_punk": {
        "name": "Solar Punk (Optimistic Eco-Future)",
        "description": "Bright future with renewable energy and harmony with nature",
        "prompt_additions": """
SCI-FI SETTING: Solar Punk (Optimistic Eco-Future)
- World: Post-scarcity society with clean energy and green technology
- Technology Level: Solar power, eco-architecture, sustainable tech
- Conflict: Maintaining utopia, external threats, philosophical debates
- Tone: Optimistic, community-focused, environmentalist

CHARACTER FOCUS:
- Engineer, community organizer, or eco-architect
- Commitment to sustainability and community
- Technological expertise with environmental focus
- Social consciousness and cooperation skills
- Optimism and problem-solving mindset
- Defender of utopian ideals

SPECIFIC DETAILS TO INCLUDE:
- Profession in sustainable society (vertical farmer, solar engineer, etc.)
- Green technology expertise
- Community role and social contributions
- Education in sustainable systems
- Living space (eco-apartment, commune, vertical garden)
- Favorite renewable tech or innovation
- Community projects they've contributed to
- Philosophy on balance between nature and technology
- What they're protecting or building
- Daily routine in utopian society
""",
    },
    
    "space_western": {
        "name": "Space Western (Frontier in Space)",
        "description": "Wild frontier setting on remote planets and space colonies",
        "prompt_additions": """
SCI-FI SETTING: Space Western (Frontier in Space)
- World: Remote space colonies, frontier planets, lawless outposts
- Technology Level: Mixed - high-tech ships, low-tech colonies
- Conflict: Frontier justice, outlaws, survival on edge of civilization
- Tone: Western tropes in space, rugged independence

CHARACTER FOCUS:
- Cowboy, bounty hunter, marshal, or frontier settler
- Self-reliance and frontier survival skills
- Rough justice and personal code of honor
- Experience with colony hardships
- Relationship with core worlds vs rim territories
- Outlaw past or law enforcement present

SPECIFIC DETAILS TO INCLUDE:
- Frontier colony or outpost they frequent
- Spaceship (often beat-up, reliable, personal)
- Weapons (mix of energy and projectile, often modified)
- Bounties they're hunting or running from
- Frontier skills (terraforming, mining, survival)
- Personal code of honor (what lines they won't cross)
- Saloon or trading post they call home
- Reputation on the frontier
- Old Earth western aesthetics in space (duster coat, hat, etc.)
- Rough frontier justice they've seen or dealt
""",
    },
}

# ============================================================================
# HISTORICAL CHARACTER PROMPTS (10 Variations)
# ============================================================================

HISTORICAL_VARIATIONS = {
    "ancient_civilizations": {
        "name": "Ancient Civilizations (Dawn of History)",
        "description": "Characters from ancient Egypt, Rome, Greece, Mesopotamia, etc.",
        "prompt_additions": """
HISTORICAL SETTING: Ancient Civilizations (Dawn of History)
- Era: 3000 BCE - 500 CE (Egypt, Mesopotamia, Greece, Rome, etc.)
- Technology Level: Bronze/Iron age, early writing, monumental architecture
- Society: City-states, empires, slavery, polytheistic religion
- Historical Context: Foundation of Western civilization, classical era

CHARACTER FOCUS:
- Social role in ancient society (citizen, slave, merchant, soldier, priest)
- Relationship with gods and religious practices
- Education level (literacy was rare and valuable)
- Classical virtues or vices
- Impact of empire, war, or conquest on their life
- Historical events they witnessed

SPECIFIC DETAILS TO INCLUDE:
- Specific civilization (Egyptian, Greek, Roman, Persian, etc.)
- Social class and legal status (citizen, freedman, slave, patrician, plebeian)
- Occupation typical of the era (gladiator, philosopher, scribe, legionnaire)
- Religious practices and patron deity
- Education (most were illiterate; if educated, where and what)
- Toga, chiton, or period-appropriate clothing
- Historical events in their lifetime (wars, emperor deaths, etc.)
- Views on the empire/city-state
- Daily life details (meals, bathing, social customs)
- What they think about the "barbarians"
""",
    },
    
    "medieval_period": {
        "name": "Medieval Period (Knights & Castles)",
        "description": "European Middle Ages, feudalism, knights, and crusades",
        "prompt_additions": """
HISTORICAL SETTING: Medieval Period (Knights & Castles)
- Era: 500 - 1500 CE (Early to Late Middle Ages)
- Technology Level: Castles, knights, feudalism, limited literacy
- Society: Feudal hierarchy, Catholic Church dominance, manorialism
- Historical Context: Crusades, Black Death, rise of kingdoms

CHARACTER FOCUS:
- Position in feudal hierarchy (serf, freeman, knight, noble, clergy)
- Relationship with the Church and religious devotion
- Chivalric code or practical survival
- Impact of wars, plagues, or crusades
- Guild membership or feudal obligations
- Medieval worldview and superstitions

SPECIFIC DETAILS TO INCLUDE:
- Specific region (England, France, Holy Roman Empire, etc.)
- Social class (peasant, merchant, knight, noble, clergy)
- Feudal obligations or lord they serve
- Religious devotion level and church attendance
- If knight: order, vows, and combat training
- Guild membership (if craftsman or merchant)
- Impact of Black Death, crusades, or Hundred Years War
- Medieval clothing (tunics, robes, armor for class)
- Literacy (rare except clergy and nobility)
- Superstitions and beliefs they hold
- Manor, village, or castle they're connected to
""",
    },
    
    "renaissance": {
        "name": "Renaissance (Rebirth of Learning)",
        "description": "European Renaissance: art, science, humanism, exploration",
        "prompt_additions": """
HISTORICAL SETTING: Renaissance (Rebirth of Learning)
- Era: 1400 - 1600 CE (Italian and Northern Renaissance)
- Technology Level: Printing press, perspective art, early science
- Society: Rise of merchant class, patronage, humanism
- Historical Context: Age of exploration, Protestant Reformation

CHARACTER FOCUS:
- Renaissance ideals: humanism, individualism, education
- Patronage relationships (supporting or being supported by wealthy)
- Artistic, scientific, or philosophical pursuits
- Impact of printing press on knowledge spread
- Religious turmoil (Catholic vs Protestant)
- Exploration and new world discoveries

SPECIFIC DETAILS TO INCLUDE:
- Specific city (Florence, Venice, Rome, London, etc.)
- Patronage relationships (Medici, Church, etc.)
- Renaissance profession (artist, scholar, merchant, explorer)
- Artistic or scientific skills
- Position on Protestant Reformation
- Knowledge of "New World" and opinions on exploration
- Books they've read (newly accessible due to printing press)
- Renaissance clothing (elaborate, fashionable)
- Classical learning and languages (Latin, Greek)
- Humanist philosophy vs traditional Catholic teaching
- Famous contemporaries they've met (da Vinci, Michelangelo, etc.)
""",
    },
    
    "age_of_exploration": {
        "name": "Age of Exploration (Discovering New Worlds)",
        "description": "European exploration and colonization of the Americas, Asia, Africa",
        "prompt_additions": """
HISTORICAL SETTING: Age of Exploration (Discovering New Worlds)
- Era: 1500 - 1700 CE
- Technology Level: Ocean-going ships, navigation tools, firearms
- Society: Colonial empires, mercantilism, indigenous encounters
- Historical Context: Columbian exchange, colonization, triangular trade

CHARACTER FOCUS:
- Explorer, colonist, indigenous person, or merchant
- Motivations (gold, glory, God, or survival)
- Cultural encounters and clashes
- Naval skills or indigenous knowledge
- Impact of disease, warfare, and exchange
- Moral stance on colonization

SPECIFIC DETAILS TO INCLUDE:
- National origin or indigenous nation
- Occupation (sailor, conquistador, missionary, trader, indigenous leader)
- Ships they've sailed on or encountered
- Continents/oceans they've crossed
- New World goods (tobacco, spices, gold, etc.)
- Diseases encountered or survived
- Indigenous peoples encountered (if European) or colonizers faced (if indigenous)
- Religious mission or commercial motivation
- Navigation skills and tools
- Period clothing (sailor, soldier, indigenous dress)
- Stance on treatment of indigenous peoples
""",
    },
    
    "industrial_revolution": {
        "name": "Industrial Revolution (Age of Industry)",
        "description": "Transformation from agrarian to industrial society",
        "prompt_additions": """
HISTORICAL SETTING: Industrial Revolution (Age of Industry)
- Era: 1760 - 1840 CE
- Technology Level: Steam power, factories, railways, telegraphs
- Society: Urbanization, working class emergence, child labor
- Historical Context: Dramatic social and economic transformation

CHARACTER FOCUS:
- Factory worker, industrialist, inventor, or displaced rural worker
- Impact of industrialization on their life
- Urban poverty vs new opportunities
- Labor rights and working conditions
- Invention and innovation
- Social change and class consciousness

SPECIFIC DETAILS TO INCLUDE:
- Occupation (factory worker, mill owner, engineer, inventor)
- Working conditions and hours
- Industrial city they live in (Manchester, Birmingham, etc.)
- Impact on traditional crafts/agriculture
- Exposure to new technologies (steam engines, railways)
- Health effects (pollution, factory accidents)
- Social class and mobility
- Union involvement or factory ownership
- Clothing (working class vs industrialist)
- Position on child labor and reforms
- How machines changed their world
""",
    },
    
    "victorian_era": {
        "name": "Victorian Era (Empire & Etiquette)",
        "description": "British Victorian period: propriety, empire, and industrial peak",
        "prompt_additions": """
HISTORICAL SETTING: Victorian Era (Empire & Etiquette)
- Era: 1837 - 1901 CE (reign of Queen Victoria)
- Technology Level: Railways, telegraphs, photography, early electricity
- Society: Strict social codes, British Empire peak, class stratification
- Historical Context: Industrial maturity, colonial expansion, rigid morality

CHARACTER FOCUS:
- British class system (working class, middle class, aristocracy)
- Victorian morality and propriety (or rebellion against it)
- Empire connections (colonial service, trade)
- Technological progress and Victorian innovations
- Gender roles (particularly restrictive for women)
- Social reform movements

SPECIFIC DETAILS TO INCLUDE:
- Specific social class and occupation
- Victorian clothing (crinolines, top hats, working clothes)
- Relationship to British Empire (support, profit, service, critique)
- Adherence to Victorian moral codes (or secret transgressions)
- Use of new technology (telegraph, railway, photography)
- Gender expectations and whether they conform
- London neighborhoods or provincial locations
- Domestic service (servants, employers, or neither)
- Social events (balls, salons, music halls depending on class)
- Position on social issues (workhouses, women's rights, imperialism)
- Reading habits (sensation novels, newspapers, improving literature)
""",
    },
    
    "world_wars_era": {
        "name": "World Wars Era (The Great Conflicts)",
        "description": "WWI and WWII: total war, technological warfare, home front",
        "prompt_additions": """
HISTORICAL SETTING: World Wars Era (The Great Conflicts)
- Era: 1914 - 1945 (WWI and WWII)
- Technology Level: Machine guns, tanks, aircraft, early computers, atomic weapons
- Society: Total war, home front mobilization, women in workforce
- Historical Context: Most destructive wars in history, Holocaust, atomic age

CHARACTER FOCUS:
- Soldier, resistance fighter, home front worker, or civilian survivor
- Trauma and psychological impact of total war
- Moral choices in extreme circumstances
- Loss and sacrifice
- Nationalism vs pacifism
- Witnessing history's darkest hours

SPECIFIC DETAILS TO INCLUDE:
- National origin and allegiance (Allied, Axis, occupied, neutral)
- Military service (if applicable): branch, rank, battles
- Civilian occupation during wartime
- War experiences: combat, occupation, bombing, rationing
- Lost loved ones and how it changed them
- Resistance activities or collaboration
- Technological warfare witnessed (tanks, planes, atomic bomb)
- PTSD or psychological effects
- Propaganda exposure and beliefs
- Knowledge of Holocaust (during or after)
- Period-appropriate clothing and gear
- How the war changed their worldview
""",
    },
    
    "cold_war": {
        "name": "Cold War Era (Superpowers & Spies)",
        "description": "Cold War: ideological conflict, nuclear threat, space race",
        "prompt_additions": """
HISTORICAL SETTING: Cold War Era (Superpowers & Spies)
- Era: 1947 - 1991 (Iron Curtain to Soviet collapse)
- Technology Level: Nuclear weapons, space race, early computers
- Society: Capitalism vs Communism, proxy wars, nuclear fear
- Historical Context: MAD doctrine, espionage, ideological warfare

CHARACTER FOCUS:
- Spy, diplomat, scientist, or citizen in divided world
- Ideological commitment (capitalist, communist, or disillusioned)
- Nuclear anxiety and existential threat
- Loyalty vs conscience
- Proxy wars and interventions
- Space race excitement or fear

SPECIFIC DETAILS TO INCLUDE:
- Side of Iron Curtain (NATO, Warsaw Pact, Non-Aligned)
- Occupation (spy, scientist, military, civilian)
- Exposure to propaganda (from both sides)
- Duck-and-cover drills and nuclear fear
- Space race enthusiasm (Sputnik, Moon landing)
- McCarthyism or Soviet purges impact
- Berlin Wall significance to them
- Proxy war involvement (Korea, Vietnam, Afghanistan)
- Espionage training or counter-intelligence
- Period culture (rock and roll vs Soviet realism)
- Position on nuclear weapons
- How they experienced key events (Cuban Missile Crisis, etc.)
""",
    },
    
    "ancient_asia": {
        "name": "Ancient Asia (Eastern Civilizations)",
        "description": "Ancient China, Japan, India, and other Asian civilizations",
        "prompt_additions": """
HISTORICAL SETTING: Ancient Asia (Eastern Civilizations)
- Era: Various (Ancient China, feudal Japan, Mauryan India, etc.)
- Technology Level: Varying by period (silk, paper, gunpowder, steel)
- Society: Imperial courts, caste systems, warrior codes, philosophy
- Historical Context: Silk Road, dynastic cycles, religious development

CHARACTER FOCUS:
- Position in Asian social hierarchy (emperor, samurai, merchant, peasant, untouchable)
- Eastern philosophy (Confucianism, Buddhism, Taoism, Hinduism, Bushido)
- Martial arts or scholarly pursuits
- Honor codes and family obligations
- Imperial service or rebellion
- Cultural refinement (tea ceremony, calligraphy, poetry)

SPECIFIC DETAILS TO INCLUDE:
- Specific civilization and dynasty (Han China, Edo Japan, Gupta India)
- Social class and occupation
- Philosophical or religious beliefs
- Martial arts training (if applicable)
- Calligraphy, poetry, or scholarly arts
- Honor code and family obligations
- Imperial examinations (China) or caste duty (India) or Bushido (Japan)
- Traditional clothing appropriate to culture and class
- Master they serve or philosophy they follow
- Cultural arts practiced (tea ceremony, meditation, etc.)
- Position in Silk Road trade networks
- How they view "foreign barbarians"
""",
    },
    
    "pre_colonial_americas": {
        "name": "Pre-Colonial Americas (Indigenous Nations)",
        "description": "Americas before European contact: Aztec, Maya, Inca, and other nations",
        "prompt_additions": """
HISTORICAL SETTING: Pre-Colonial Americas (Indigenous Nations)
- Era: Pre-1492 (before European contact)
- Technology Level: Advanced architecture, astronomy, agriculture (no iron/wheel)
- Society: Complex civilizations, city-states, tribal confederations
- Historical Context: Rich cultures before colonization

CHARACTER FOCUS:
- Member of specific indigenous nation
- Connection to land and spiritual beliefs
- Role in community (warrior, priest, farmer, artisan)
- Oral traditions and ancestral knowledge
- Astronomical and agricultural expertise
- Complex social structures of their civilization

SPECIFIC DETAILS TO INCLUDE:
- Specific nation (Aztec, Maya, Inca, Iroquois, Navajo, etc.)
- Role in society (noble, priest, warrior, farmer, artisan)
- Spiritual beliefs and ceremonies
- Astronomical knowledge
- Agricultural techniques (chinampas, terracing, three sisters)
- Traditional clothing and adornments
- Architectural knowledge (pyramids, pueblos, longhouses)
- Oral traditions and stories they know
- Ceremonial practices and religious role
- Seasonal cycles and their significance
- Relationships with neighboring nations
- Pre-Columbian worldview (no knowledge of Europe, Asia, Africa)
""",
    },
}

# ============================================================================
# HORROR CHARACTER PROMPTS (5 Variations)
# ============================================================================

HORROR_VARIATIONS = {
    "gothic_horror": {
        "name": "Gothic Horror (Classic Terror)",
        "description": "Atmospheric dread, haunted locations, psychological terror",
        "prompt_additions": """
HORROR SETTING: Gothic Horror (Classic Terror)
- World: Fog-shrouded estates, crumbling castles, cursed bloodlines
- Threat Level: Ancient evils, family curses, vengeful spirits
- Atmosphere: Oppressive dread, Victorian aesthetics, creeping madness
- Tone: Atmospheric, psychological, elegantly horrifying

CHARACTER FOCUS:
- Connection to cursed family lines or haunted locations
- Psychological fragility or mental deterioration
- Dark secrets, forbidden knowledge, or terrible inheritance
- Period-appropriate attire (Victorian, Edwardian)
- Relationships with the supernatural (medium, investigator, victim)
- Internal conflict between reason and terror

SPECIFIC DETAILS TO INCLUDE:
- Family history of tragedy or curse
- Phobias, fears, or psychological vulnerabilities
- Knowledge of occult or forbidden lore
- Physical or mental scars from supernatural encounters
- Relationships with other victims or investigators
""",
    },
    
    "cosmic_horror": {
        "name": "Cosmic Horror (Lovecraftian)",
        "description": "Incomprehensible entities, existential dread, sanity-shattering truths",
        "prompt_additions": """
HORROR SETTING: Cosmic Horror (Lovecraftian)
- World: Reality is thin, ancient beings lurk beyond comprehension
- Threat Level: Cosmic entities that defy understanding
- Atmosphere: Existential dread, inevitable doom, insignificance
- Tone: Cerebral, philosophical, sanity-eroding

CHARACTER FOCUS:
- Scholar, investigator, or unwitting discoverer of forbidden truths
- Gradual realization of humanity's cosmic insignificance
- Mental deterioration from exposure to incomprehensible horrors
- Obsessive pursuit of knowledge despite the cost
- Cultist connections or opposition to dark cults
- Witnesses to reality-breaking phenomena

SPECIFIC DETAILS TO INCLUDE:
- Academic background (archaeology, occult studies, astronomy)
- Sanity deterioration markers (nightmares, paranoia, obsession)
- Encounters with impossible geometry or non-Euclidean spaces
- Knowledge of ancient languages or forbidden texts
- Physical transformations from cosmic exposure
""",
    },
    
    "survival_horror": {
        "name": "Survival Horror (Fight or Flight)",
        "description": "Resource scarcity, constant danger, desperate survival",
        "prompt_additions": """
HORROR SETTING: Survival Horror (Fight or Flight)
- World: Isolated location, cut off from help, limited resources
- Threat Level: Persistent danger, limited combat capability
- Atmosphere: Claustrophobic tension, resource management stress
- Tone: Desperate, visceral, survival-focused

CHARACTER FOCUS:
- Ordinary person thrust into extraordinary danger
- Practical survival skills (medical, mechanical, tactical)
- Psychological resilience and breaking points
- Resource management mindset
- Relationships with other survivors (trust, betrayal)
- Physical injuries and limitations

SPECIFIC DETAILS TO INCLUDE:
- Survival skills and practical knowledge
- Physical condition and injuries
- Inventory of useful items or weapons
- Psychological state (fear, determination, paranoia)
- Relationship dynamics with other survivors
""",
    },
    
    "folk_horror": {
        "name": "Folk Horror (Rural Nightmare)",
        "description": "Pagan rituals, isolated communities, nature's vengeance",
        "prompt_additions": """
HORROR SETTING: Folk Horror (Rural Nightmare)
- World: Remote villages, ancient traditions, nature's dark side
- Threat Level: Pagan entities, cult rituals, seasonal sacrifices
- Atmosphere: Rustic unease, tradition vs modernity, rural isolation
- Tone: Unsettling, ritualistic, nature-focused

CHARACTER FOCUS:
- Outsider discovering dark community secrets, or local initiated into mysteries
- Connection to land, seasons, and ancient traditions
- Conflict between modern rationality and old ways
- Participation in or resistance to dark rituals
- Knowledge of folk customs and pagan lore
- Relationship with nature (respect, fear, communion)

SPECIFIC DETAILS TO INCLUDE:
- Rural background or outsider perspective
- Knowledge of folklore, herbs, and seasonal rites
- Role in community (elder, initiate, skeptic, victim)
- Connection to specific location or sacred site
- Physical markers of ritual participation (scars, tattoos, offerings)
""",
    },
    
    "body_horror": {
        "name": "Body Horror (Biological Nightmare)",
        "description": "Physical transformation, visceral grotesquery, loss of bodily autonomy",
        "prompt_additions": """
HORROR SETTING: Body Horror (Biological Nightmare)
- World: Medical facilities, scientific experiments, biological outbreaks
- Threat Level: Physical transformation, viral infection, genetic mutation
- Atmosphere: Visceral disgust, loss of identity, transformation terror
- Tone: Grotesque, medical, identity-crisis focused

CHARACTER FOCUS:
- Undergoing or resisting physical transformation
- Medical background or experimental subject
- Body dysmorphia or transformation anxiety
- Struggle to maintain humanity during change
- Relationships affected by physical alteration
- Scientific curiosity vs ethical horror

SPECIFIC DETAILS TO INCLUDE:
- Current physical state and ongoing transformations
- Medical or scientific knowledge
- Psychological response to bodily changes
- Attempts to reverse or control transformation
- Relationships before and after physical changes
""",
    },
}

# ============================================================================
# MYSTERY/THRILLER CHARACTER PROMPTS (5 Variations)
# ============================================================================

MYSTERY_THRILLER_VARIATIONS = {
    "detective_noir": {
        "name": "Detective Noir (Hard-Boiled)",
        "description": "Cynical investigator, urban corruption, femme fatales",
        "prompt_additions": """
MYSTERY SETTING: Detective Noir (Hard-Boiled)
- World: Rain-soaked streets, smoke-filled rooms, urban decay
- Crime Level: Murder, corruption, organized crime
- Atmosphere: Cynical, atmospheric, morally grey
- Tone: Hard-boiled, world-weary, cigarette-stained

CHARACTER FOCUS:
- Private investigator, detective, or journalist
- Cynical worldview from years of seeing humanity's worst
- Complex relationship with law enforcement (ally, rival, or corrupt)
- Personal code of ethics in an immoral world
- Troubled past (failed relationships, lost cases, personal demons)
- Sharp wit and observational skills

SPECIFIC DETAILS TO INCLUDE:
- Investigative methodology and signature techniques
- Vices (drinking, smoking, gambling)
- Network of informants and contacts
- Office or workspace details (dusty, cramped, lived-in)
- Relationship with police, criminals, and clients
""",
    },
    
    "psychological_thriller": {
        "name": "Psychological Thriller (Mind Games)",
        "description": "Unreliable narrator, gaslighting, perception vs reality",
        "prompt_additions": """
MYSTERY SETTING: Psychological Thriller (Mind Games)
- World: Everyday settings hiding dark secrets
- Threat Level: Mental manipulation, psychological warfare
- Atmosphere: Paranoia, doubt, shifting reality
- Tone: Unsettling, cerebral, twist-laden

CHARACTER FOCUS:
- Unreliable perception or memory issues
- Gaslit by others or questioning own sanity
- Intelligence matched against manipulator
- Past trauma affecting present perception
- Isolation from potential allies
- Obsessive personality traits

SPECIFIC DETAILS TO INCLUDE:
- Mental health history or current issues
- Specific triggers or phobias
- Relationships with manipulative individuals
- Coping mechanisms (healthy or destructive)
- Evidence of manipulation (journals, recordings, witnesses)
""",
    },
    
    "conspiracy_thriller": {
        "name": "Conspiracy Thriller (Paranoid Truth)",
        "description": "Government cover-ups, shadowy organizations, dangerous knowledge",
        "prompt_additions": """
MYSTERY SETTING: Conspiracy Thriller (Paranoid Truth)
- World: Shadowy agencies, global conspiracies, hidden truths
- Threat Level: Powerful organizations, surveillance, assassination
- Atmosphere: Paranoid, no one to trust, layers of deception
- Tone: Fast-paced, revelatory, ever-escalating

CHARACTER FOCUS:
- Whistleblower, investigator, or accidental discoverer of secrets
- Technical skills (hacking, encryption, investigation)
- Paranoia justified by real threats
- Network of allies and uncertain loyalties
- Pursued by powerful forces
- Moral conflict about exposing truth vs safety

SPECIFIC DETAILS TO INCLUDE:
- Area of expertise (journalism, programming, intelligence)
- Methods of information gathering
- Personal security measures
- Who's hunting them and why
- Evidence collected and hidden
""",
    },
    
    "cozy_mystery": {
        "name": "Cozy Mystery (Amateur Sleuth)",
        "description": "Small-town murder, amateur detective, low violence",
        "prompt_additions": """
MYSTERY SETTING: Cozy Mystery (Amateur Sleuth)
- World: Quaint villages, bookshops, tea rooms, tight-knit communities
- Crime Level: Murder (but off-screen), theft, blackmail
- Atmosphere: Charming setting, darker undercurrents, community secrets
- Tone: Light-hearted despite death, puzzle-focused, character-driven

CHARACTER FOCUS:
- Amateur detective with day job (librarian, baker, teacher)
- Natural curiosity and observational skills
- Deep community connections and gossip network
- Non-violent problem-solving approach
- Quirky hobbies or special knowledge
- Relationships with recurring cast (friendly cop, suspect, rival)

SPECIFIC DETAILS TO INCLUDE:
- Profession and how it aids investigations
- Personality quirks and charming traits
- Social network within community
- Special knowledge (history, psychology, crafts)
- Relationship with local law enforcement
""",
    },
    
    "legal_thriller": {
        "name": "Legal Thriller (Courtroom Drama)",
        "description": "Legal battles, courtroom intrigue, justice vs law",
        "prompt_additions": """
MYSTERY SETTING: Legal Thriller (Courtroom Drama)
- World: Courtrooms, law offices, legal system complexities
- Conflict: Legal battles, ethical dilemmas, procedural warfare
- Atmosphere: High-stakes litigation, career-defining cases
- Tone: Intellectual combat, moral complexity, dramatic reveals

CHARACTER FOCUS:
- Lawyer (defense, prosecution, or civil), judge, or legal investigator
- Passionate about justice or cynical about system
- Exceptional legal mind and rhetorical skills
- Work-life balance struggles
- Ethical dilemmas (letter of law vs spirit of justice)
- Mentors, rivals, and allies in legal world

SPECIFIC DETAILS TO INCLUDE:
- Legal specialization and notable cases
- Courtroom style and strategies
- Personal stakes in current case
- Relationships with colleagues and opponents
- Ethical boundaries and compromises
""",
    },
}

# ============================================================================
# ROMANCE CHARACTER PROMPTS (5 Variations)
# ============================================================================

ROMANCE_VARIATIONS = {
    "contemporary_romance": {
        "name": "Contemporary Romance (Modern Love)",
        "description": "Modern settings, real-world relationships, emotional growth",
        "prompt_additions": """
ROMANCE SETTING: Contemporary Romance (Modern Love)
- World: Modern cities, workplaces, everyday locations
- Relationship: Realistic obstacles, personal growth, communication
- Atmosphere: Warm, relatable, emotionally authentic
- Tone: Heartfelt, hopeful, character-driven

CHARACTER FOCUS:
- Relatable modern person with career, friends, family
- Past relationship trauma or baggage
- Personal growth arc through relationship
- Clear desires, fears, and vulnerabilities
- Work-life balance struggles
- Authentic emotional expression

SPECIFIC DETAILS TO INCLUDE:
- Career and how it affects relationships
- Past relationships and lessons learned
- Emotional wounds and healing needs
- Love language and communication style
- Support network (friends, family)
""",
    },
    
    "paranormal_romance": {
        "name": "Paranormal Romance (Supernatural Love)",
        "description": "Vampires, shifters, fae—forbidden supernatural attraction",
        "prompt_additions": """
ROMANCE SETTING: Paranormal Romance (Supernatural Love)
- World: Hidden supernatural communities within modern world
- Relationship: Forbidden attraction, species barriers, danger
- Atmosphere: Mystical, dangerous, intensely passionate
- Tone: Dramatic, sensual, stakes-filled

CHARACTER FOCUS:
- Human discovering supernatural world, or supernatural being
- Species-specific traits (vampire allure, shifter pack dynamics, fae glamour)
- Forbidden nature of relationship (species, rival groups, laws)
- Supernatural powers or vulnerabilities
- Divided loyalties (love vs duty/pack/coven)
- Immortality concerns or mortal dangers

SPECIFIC DETAILS TO INCLUDE:
- Supernatural nature and associated powers
- How they discovered/hide their nature
- Community rules about inter-species relationships
- Supernatural enemies or political complications
- Physical manifestations of supernatural nature
""",
    },
    
    "historical_romance": {
        "name": "Historical Romance (Period Love)",
        "description": "Regency, Victorian, or historical era romance with period constraints",
        "prompt_additions": """
ROMANCE SETTING: Historical Romance (Period Love)
- World: Historical period (specify: Regency, Victorian, Medieval, etc.)
- Relationship: Social class barriers, reputation, propriety
- Atmosphere: Period-appropriate manners, societal pressure
- Tone: Longing, scandal, social navigation

CHARACTER FOCUS:
- Period-appropriate social standing (nobility, merchant class, servant)
- Adherence to or rebellion against social norms
- Reputation concerns and scandal potential
- Family expectations and duty
- Period-specific accomplishments (music, riding, swordplay)
- Secret desires vs public persona

SPECIFIC DETAILS TO INCLUDE:
- Exact historical period and location
- Social status and expectations
- Period-appropriate skills and education
- Family pressure and arranged matches
- Reputation stakes and scandal risks
""",
    },
    
    "romantic_comedy": {
        "name": "Romantic Comedy (Meet-Cute Love)",
        "description": "Humorous situations, witty banter, heartwarming connections",
        "prompt_additions": """
ROMANCE SETTING: Romantic Comedy (Meet-Cute Love)
- World: Charming locations, awkward situations, comedy of errors
- Relationship: Misunderstandings, witty banter, opposites attract
- Atmosphere: Light-hearted, humorous, endearing
- Tone: Funny, warm, optimistic

CHARACTER FOCUS:
- Quirky personality traits and endearing flaws
- Comedic misunderstandings and mishaps
- Sharp wit and banter capabilities
- Relatable awkwardness and insecurities
- Close friends providing comic relief and advice
- Career or life situation ripe for comedy

SPECIFIC DETAILS TO INCLUDE:
- Specific quirks and comedy-enabling traits
- Embarrassing moments and awkward tendencies
- Witty comebacks and verbal sparring style
- Circle of comedic supporting characters
- Comedic obstacles to relationship
""",
    },
    
    "second_chance_romance": {
        "name": "Second Chance Romance (Lost Love)",
        "description": "Reunited lovers, past mistakes, emotional healing",
        "prompt_additions": """
ROMANCE SETTING: Second Chance Romance (Lost Love)
- World: Characters reunited after years apart
- Relationship: Unresolved past, emotional wounds, growth needed
- Atmosphere: Bittersweet, nostalgic, healing-focused
- Tone: Emotional, mature, redemptive

CHARACTER FOCUS:
- Shared history with past romantic partner
- Reasons for original separation (misunderstanding, timing, mistakes)
- Personal growth since separation
- Unresolved feelings and lingering pain
- Changed circumstances bringing them together
- Maturity and lessons learned

SPECIFIC DETAILS TO INCLUDE:
- Nature of original relationship and breakup
- How much time has passed
- What each has done in intervening years
- Remaining emotional wounds
- Current circumstances forcing reunion
""",
    },
}

# ============================================================================
# ADVENTURE CHARACTER PROMPTS (5 Variations)
# ============================================================================

ADVENTURE_VARIATIONS = {
    "treasure_hunter": {
        "name": "Treasure Hunter (Indiana Jones Style)",
        "description": "Archaeological adventures, ancient puzzles, rival treasure seekers",
        "prompt_additions": """
ADVENTURE SETTING: Treasure Hunter (Archaeological Action)
- World: Ancient ruins, hidden temples, archaeological sites
- Quest: Lost artifacts, legendary treasures, historical mysteries
- Atmosphere: Exotic locales, death traps, rival seekers
- Tone: Adventurous, witty, action-packed

CHARACTER FOCUS:
- Archaeologist, historian, or professional treasure hunter
- Knowledge of ancient civilizations and languages
- Physical fitness for climbing, exploring, fighting
- Rivals and allies in treasure-hunting world
- Moral code about preservation vs profit
- Signature equipment and tools

SPECIFIC DETAILS TO INCLUDE:
- Area of historical expertise
- Famous finds or notable failures
- Signature gear (whip, maps, tools)
- Network of contacts and information sources
- Nemesis or rival treasure hunter
""",
    },
    
    "survival_adventure": {
        "name": "Survival Adventure (Into the Wild)",
        "description": "Wilderness survival, natural challenges, self-discovery",
        "prompt_additions": """
ADVENTURE SETTING: Survival Adventure (Wilderness Challenge)
- World: Untamed wilderness, harsh environments, nature's power
- Challenge: Survival against elements, dangerous wildlife
- Atmosphere: Raw nature, self-reliance, primal struggle
- Tone: Gritty, introspective, human vs nature

CHARACTER FOCUS:
- Survival skills (fire, shelter, water, food)
- Physical endurance and mental resilience
- Reason for being in wilderness (choice, accident, mission)
- Relationship with nature (respect, fear, dominance)
- Internal journey paralleling physical survival
- Minimal equipment philosophy

SPECIFIC DETAILS TO INCLUDE:
- Specific survival skills and knowledge
- Physical condition and adaptations
- Mental state and coping strategies
- Equipment carried and improvised
- Wildlife encounters and responses
""",
    },
    
    "heist_adventure": {
        "name": "Heist Adventure (Master Thief)",
        "description": "Elaborate plans, specialized skills, one big score",
        "prompt_additions": """
ADVENTURE SETTING: Heist Adventure (The Big Score)
- World: High-security locations, criminal underworld, planning stages
- Objective: Impossible theft, intricate planning, team coordination
- Atmosphere: Tension, precision timing, backup plans
- Tone: Clever, stylish, team-focused

CHARACTER FOCUS:
- Specialized role (mastermind, safecracker, con artist, muscle, hacker)
- Unique skills perfected over years
- Past heists (successes and failures)
- Team dynamics and trust issues
- Code of honor among thieves
- Personal motivation for this particular job

SPECIFIC DETAILS TO INCLUDE:
- Specific heist specialty and skills
- Tools of the trade
- Signature techniques or style
- Relationships with crew members
- Stakes if caught or if heist fails
""",
    },
    
    "exploration_adventure": {
        "name": "Exploration Adventure (Uncharted Territories)",
        "description": "Discovering new lands, first contact, mapping the unknown",
        "prompt_additions": """
ADVENTURE SETTING: Exploration Adventure (Uncharted Lands)
- World: Unexplored regions, unknown civilizations, geographical mysteries
- Mission: Discovery, mapping, scientific study, first contact
- Atmosphere: Wonder, danger, isolation, discovery
- Tone: Curious, respectful, pioneering

CHARACTER FOCUS:
- Explorer, scientist, cartographer, or expedition member
- Curiosity balanced with caution
- Scientific or geographical expertise
- Leadership or teamwork skills
- Respect for or exploitation of discoveries
- Documentation and observation focus

SPECIFIC DETAILS TO INCLUDE:
- Exploration specialization (biology, geography, anthropology)
- Equipment for documentation and survival
- Expedition role and responsibilities
- Previous expeditions and discoveries
- Ethical approach to new discoveries
""",
    },
    
    "sky_adventure": {
        "name": "Sky Adventure (Airship & Aviation)",
        "description": "Flying machines, aerial combat, sky pirates and kingdoms",
        "prompt_additions": """
ADVENTURE SETTING: Sky Adventure (Aerial Action)
- World: Floating islands, airship trade routes, sky kingdoms
- Transport: Airships, flying machines, personal flight devices
- Atmosphere: Freedom of flight, aerial combat, clouds and storms
- Tone: Swashbuckling, atmospheric, vertigo-inducing

CHARACTER FOCUS:
- Pilot, sky pirate, airship crew, or aerial courier
- Aviation skills and mechanical knowledge
- Comfort with heights and aerial maneuvering
- Relationships in flying communities
- Adventures at various altitudes
- Signature aircraft or vessel

SPECIFIC DETAILS TO INCLUDE:
- Piloting skills and specialization
- Personal aircraft details
- Aerial combat experience
- Fear of heights overcome or embraced
- Sky-faring culture knowledge
""",
    },
}

# ============================================================================
# WESTERN CHARACTER PROMPTS (3 Variations)
# ============================================================================

WESTERN_VARIATIONS = {
    "classic_western": {
        "name": "Classic Western (Frontier Justice)",
        "description": "Cowboys, outlaws, frontier towns, Old West adventure",
        "prompt_additions": """
WESTERN SETTING: Classic Western (Old West)
- World: American frontier (1860s-1890s), lawless territories
- Conflict: Outlaws vs lawmen, settlers vs bandits, honor codes
- Atmosphere: Dusty streets, saloons, wide open spaces
- Tone: Stoic, honorable, action-driven

CHARACTER FOCUS:
- Gunslinger, lawman, outlaw, rancher, or drifter
- Shooting skills and quick-draw reputation
- Personal code of honor in lawless land
- Past defining them (war veteran, reformed outlaw, revenge seeker)
- Horse as trusted companion
- Few words, decisive actions

SPECIFIC DETAILS TO INCLUDE:
- Gun skills and signature weapon
- Reputation in various towns
- Horse details and bond
- Western attire specifics (hat, boots, duster)
- Past events driving current path
""",
    },
    
    "weird_western": {
        "name": "Weird Western (Frontier Fantasy)",
        "description": "Old West meets supernatural, steampunk, or magic",
        "prompt_additions": """
WESTERN SETTING: Weird Western (Supernatural Frontier)
- World: Old West infused with magic, monsters, or advanced technology
- Conflict: Supernatural threats, mad science, mystical outlaws
- Atmosphere: Western aesthetics meet impossible elements
- Tone: Genre-blending, imaginative, anachronistic

CHARACTER FOCUS:
- Traditional western role enhanced by supernatural/tech element
- Magic user, monster hunter, or steampunk inventor in Old West
- Dealing with both mundane and supernatural threats
- Unique weapons blending tech and tradition
- Knowledge of occult or advanced science
- Straddling two worlds (ordinary and extraordinary)

SPECIFIC DETAILS TO INCLUDE:
- Nature of weird element (magic, tech, supernatural)
- How they acquired unusual abilities/knowledge
- Specialized equipment or weapons
- Reputation in both normal and weird circles
- Conflicts between Old West values and new possibilities
""",
    },
    
    "modern_western": {
        "name": "Modern Western (Contemporary Frontier)",
        "description": "Western themes in modern/contemporary setting",
        "prompt_additions": """
WESTERN SETTING: Modern Western (Contemporary)
- World: Modern rural West, ranches, small towns, desert landscapes
- Conflict: Modern issues with Western sensibilities
- Atmosphere: Traditional values meet contemporary challenges
- Tone: Neo-western, character-study, landscape-focused

CHARACTER FOCUS:
- Modern rancher, sheriff, drifter, or rodeo performer
- Traditional skills in contemporary world
- Tension between old ways and modern life
- Connection to land and frontier heritage
- Pickup truck as modern horse
- Fewer words, more action still applies

SPECIFIC DETAILS TO INCLUDE:
- Modern profession with western roots
- Traditional skills still practiced
- Contemporary challenges faced
- Vehicle and modern equipment
- Balance of tradition and modernity
""",
    },
}

# ============================================================================
# DYSTOPIAN CHARACTER PROMPTS (5 Variations)
# ============================================================================

DYSTOPIAN_VARIATIONS = {
    "totalitarian_dystopia": {
        "name": "Totalitarian Dystopia (1984-Style)",
        "description": "Oppressive government, surveillance state, thought control",
        "prompt_additions": """
DYSTOPIAN SETTING: Totalitarian Dystopia (Orwellian)
- World: All-powerful government, constant surveillance, propaganda
- Conflict: Individual freedom vs state control, rebellion vs compliance
- Atmosphere: Paranoid, oppressive, grey and uniform
- Tone: Political, psychological, resistance-focused

CHARACTER FOCUS:
- Role in system (party member, rebel, citizen, enforcer)
- Awareness of oppression (awakening, always knew, actively denying)
- Surveillance paranoia and doublethink
- Secret rebellion or public compliance
- Loss of identity and personhood
- Relationships tested by ideology

SPECIFIC DETAILS TO INCLUDE:
- Official position in society
- Secret thoughts vs public persona
- Methods of resistance or survival
- Relationships under state scrutiny
- Awareness of historical truth vs propaganda
""",
    },
    
    "environmental_dystopia": {
        "name": "Environmental Dystopia (Climate Collapse)",
        "description": "Ecological disaster, resource wars, survival adaptation",
        "prompt_additions": """
DYSTOPIAN SETTING: Environmental Dystopia (Eco-Collapse)
- World: Climate catastrophe, scarce resources, environmental refugees
- Conflict: Survival in harsh environment, resource conflicts
- Atmosphere: Polluted, extreme weather, desperate adaptation
- Tone: Survivalist, ecological, resource-focused

CHARACTER FOCUS:
- Survival skills in hostile environment
- Role in resource economy (scavenger, trader, guardian)
- Adaptation to climate extremes
- Memory of better times vs acceptance of new normal
- Environmental knowledge and sustainability skills
- Community bonds under resource stress

SPECIFIC DETAILS TO INCLUDE:
- Specific environmental challenges faced
- Adaptation strategies and equipment
- Resource access and trading goods
- Health effects from environmental damage
- Skills for surviving in changed climate
""",
    },
    
    "corporate_dystopia": {
        "name": "Corporate Dystopia (Mega-Corp Control)",
        "description": "Corporate rule, privatized everything, consumer culture extremes",
        "prompt_additions": """
DYSTOPIAN SETTING: Corporate Dystopia (Mega-Corp Rule)
- World: Corporations replaced governments, everything commodified
- Conflict: Worker exploitation, branded existence, economic slavery
- Atmosphere: Hyper-commercial, class stratification, synthetic
- Tone: Satirical, capitalist critique, brand-saturated

CHARACTER FOCUS:
- Corporate rank (executive, wage slave, unemployed, rebel)
- Brand loyalty or rebellion against consumerism
- Debt slavery or economic freedom quest
- Skills marketable in corporate economy
- Relationship with company (employee, subcontractor, enemy)
- Identity defined by consumption or resisting it

SPECIFIC DETAILS TO INCLUDE:
- Corporate affiliation and rank
- Economic status and debt level
- Marketable skills and resume
- Brand preferences enforced or resisted
- Methods of surviving corporate system
""",
    },
    
    "tech_dystopia": {
        "name": "Tech Dystopia (Digital Nightmare)",
        "description": "AI control, virtual reality addiction, technology dependency",
        "prompt_additions": """
DYSTOPIAN SETTING: Tech Dystopia (Digital Control)
- World: AI governance, VR escapism, human-tech fusion gone wrong
- Conflict: Humanity vs technology, digital vs physical existence
- Atmosphere: Glitching reality, screen-saturated, posthuman
- Tone: Philosophical, cyber, existential

CHARACTER FOCUS:
- Relationship with technology (addicted, resistant, merged)
- Digital presence vs physical body
- Hacking skills or technological illiteracy
- AI interactions (servant, overlord, companion)
- Virtual vs real identity crisis
- Augmentations or rejection of enhancement

SPECIFIC DETAILS TO INCLUDE:
- Technology augmentations or modifications
- Digital skills and virtual presence
- AI relationships and dependencies
- Screen time and reality disconnection
- Resistance to or embrace of tech integration
""",
    },
    
    "plague_dystopia": {
        "name": "Plague Dystopia (Pandemic World)",
        "description": "Disease-ravaged society, quarantine zones, immune vs infected",
        "prompt_additions": """
DYSTOPIAN SETTING: Plague Dystopia (Pandemic Collapse)
- World: Global pandemic, quarantine enforcement, medical martial law
- Conflict: Survival vs infection, immunity privilege, medical resources
- Atmosphere: Masked faces, empty streets, quarantine barriers
- Tone: Medical horror, survival, social breakdown

CHARACTER FOCUS:
- Immune status (immune, carrier, vulnerable, infected)
- Medical knowledge or desperate ignorance
- Quarantine enforcement or violation
- Loss from pandemic (family, community, normalcy)
- Survival strategies in plague world
- Moral choices about resource distribution

SPECIFIC DETAILS TO INCLUDE:
- Immune status and how discovered
- Medical skills or vulnerabilities
- Personal losses from pandemic
- Protective equipment and hygiene rituals
- Role in pandemic society (enforcer, caregiver, survivor)
""",
    },
}

# ============================================================================
# SUPERHERO CHARACTER PROMPTS (5 Variations)
# ============================================================================

SUPERHERO_VARIATIONS = {
    "classic_superhero": {
        "name": "Classic Superhero (Silver Age)",
        "description": "Traditional heroes, clear morality, colorful costumes, secret identities",
        "prompt_additions": """
SUPERHERO SETTING: Classic Superhero (Silver Age)
- World: Bright cities, clear good vs evil, colorful heroics
- Powers: Defined abilities, dramatic origin stories
- Atmosphere: Optimistic, adventurous, comic-book action
- Tone: Heroic, inspirational, morally clear

CHARACTER FOCUS:
- Superhero identity vs civilian identity
- Origin story of powers (accident, experiment, alien, mutation)
- Clear moral code and heroic ideals
- Arch-nemesis and rogues gallery
- Secret identity protection
- Day job as cover identity

SPECIFIC DETAILS TO INCLUDE:
- Specific superpowers and limitations
- Origin story details
- Costume design and symbolism
- Secret identity and civilian life
- Arch-enemy and their connection
""",
    },
    
    "dark_vigilante": {
        "name": "Dark Vigilante (Gritty Street-Level)",
        "description": "Urban crime-fighter, no superpowers, brutal methods, trauma-driven",
        "prompt_additions": """
SUPERHERO SETTING: Dark Vigilante (Street-Level)
- World: Crime-ridden cities, corrupt systems, street-level threats
- Powers: Mostly none—relies on skills, training, and equipment
- Atmosphere: Noir-ish, violent, psychologically complex
- Tone: Dark, brutal, morally grey

CHARACTER FOCUS:
- Traumatic origin driving vigilante mission
- Martial arts and detective skills
- Brutal but non-lethal methods (or not)
- Psychological damage from double life
- War on crime that can't be won
- Relationship with actual law enforcement

SPECIFIC DETAILS TO INCLUDE:
- Traumatic origin event
- Training and skill acquisition
- Equipment and gadgets
- Methods and ethical boundaries
- Toll of vigilante life on psyche
""",
    },
    
    "team_hero": {
        "name": "Team Hero (Avengers/X-Men Style)",
        "description": "Part of superhero team, power synergy, team dynamics",
        "prompt_additions": """
SUPERHERO SETTING: Team Hero (Super-Group)
- World: Coordinated hero teams, large-scale threats
- Powers: Unique abilities complementing team members
- Atmosphere: Collaborative, friendship-focused, training together
- Tone: Team dynamics, found family, coordinated action

CHARACTER FOCUS:
- Specific role within team (leader, powerhouse, tech, stealth)
- Powers that synergize with teammates
- Relationships within team (rivalry, romance, mentorship)
- Personal arc within team context
- Team base as second home
- Balancing individual goals with team needs

SPECIFIC DETAILS TO INCLUDE:
- Specific powers and team role
- Relationships with each teammate
- Team dynamics and your position
- Team base and shared resources
- Personal arc within team context
""",
    },
    
    "flawed_hero": {
        "name": "Flawed Hero (Tragic/Anti-Hero)",
        "description": "Powers as curse, reluctant hero, moral compromises",
        "prompt_additions": """
SUPERHERO SETTING: Flawed Hero (Tragic Powers)
- World: Powers bring as much suffering as strength
- Powers: Come with terrible costs or dark sides
- Atmosphere: Burden of power, isolation, moral complexity
- Tone: Tragic, conflicted, redemption-seeking

CHARACTER FOCUS:
- Powers as curse rather than gift
- Collateral damage and unintended consequences
- Temptation to misuse powers
- Isolation due to dangerous abilities
- Struggle to be hero despite darkness
- Redemption arc or tragic spiral

SPECIFIC DETAILS TO INCLUDE:
- Powers and their dark costs
- Incidents of powers causing harm
- Moral compromises made
- Isolation and relationship difficulties
- Path toward redemption or destruction
""",
    },
    
    "cosmic_hero": {
        "name": "Cosmic Hero (Galactic Guardian)",
        "description": "Cosmic powers, space-faring, universal threats, god-like abilities",
        "prompt_additions": """
SUPERHERO SETTING: Cosmic Hero (Universal Scale)
- World: Multiple planets, cosmic entities, universal threats
- Powers: God-like abilities, energy manipulation, cosmic awareness
- Atmosphere: Epic scale, existential stakes, alien encounters
- Tone: Philosophical, vast, awe-inspiring

CHARACTER FOCUS:
- Cosmic-level powers (energy manipulation, flight, invulnerability)
- Origin of cosmic power (alien tech, cosmic entity, transformation)
- Perspective changed by cosmic awareness
- Relationship with Earth vs universe
- Cosmic threats and entities as peers/enemies
- Struggle to relate to humanity

SPECIFIC DETAILS TO INCLUDE:
- Source and nature of cosmic powers
- Cosmic entities encountered or allied with
- Relationship with Earth after cosmic exposure
- Scale of threats typically faced
- Loneliness of cosmic existence
""",
    },
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_all_variations():
    """Get all character prompt variations organized by genre."""
    return {
        "fantasy": FANTASY_VARIATIONS,
        "sci_fi": SCI_FI_VARIATIONS,
        "historical": HISTORICAL_VARIATIONS,
        "horror": HORROR_VARIATIONS,
        "mystery_thriller": MYSTERY_THRILLER_VARIATIONS,
        "romance": ROMANCE_VARIATIONS,
        "adventure": ADVENTURE_VARIATIONS,
        "western": WESTERN_VARIATIONS,
        "dystopian": DYSTOPIAN_VARIATIONS,
        "superhero": SUPERHERO_VARIATIONS,
    }

def get_variation_by_key(genre: str, variation_key: str):
    """Get a specific variation by genre and key."""
    all_variations = get_all_variations()
    if genre in all_variations and variation_key in all_variations[genre]:
        return all_variations[genre][variation_key]
    return None

def list_all_variation_names():
    """List all available variation names for UI display."""
    all_vars = get_all_variations()
    result = {}
    for genre, variations in all_vars.items():
        result[genre] = [
            {
                "key": key,
                "name": var["name"],
                "description": var["description"]
            }
            for key, var in variations.items()
        ]
    return result

def build_enhanced_character_prompt(base_prompt: str, genre: str, variation_key: str) -> str:
    """
    Combine base character prompt with genre-specific variation enhancements.
    
    Args:
        base_prompt: The base character generation prompt
        genre: "fantasy", "sci_fi", or "historical"
        variation_key: Specific variation within the genre
        
    Returns:
        Enhanced prompt with genre-specific additions
    """
    variation = get_variation_by_key(genre, variation_key)
    if not variation:
        return base_prompt
    
    enhanced_prompt = f"""{base_prompt}

{variation['prompt_additions']}
"""
    return enhanced_prompt
