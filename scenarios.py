"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # ⚠️ PUT YOUR OWN WRITING HERE. Not AI text, not a sample from the web —
        # things you actually wrote. This is the criterion that matters most and
        # it's meaningless with someone else's prose.
        "texts": [
            "I am enjoying what I am learning withing the course AI201. This course is exposing me to lot different type of problems and each of the exercise is well thought off. Each of the excercises given in the assignement will make one think and will force one ot do lot of research before implementing the code. I am specially liking how we need to write the criteria and my whole way of thinking AI solution is changing. Now I am thinking for any solution how I can term the criteria soas the solution that I am building gives me predictab;le results.",
            "Ai is oging to change peoples lives isn more than one way. There will be lot of positive outcome and at the same time there will be  lot of negative outcomes. There will be bad actors who will take advantage of the AI and cause damage to common people by stealing or by creating chaos. While tin areas like biomedical, pharmceutical and others like medical and surgical it will usher in a new world. Since Human labor will go down so cost will go down too. AI will touch peoples lives whether they are in villages or remote areas or in cities. This will be another major change  or revolution like industrial revolution",
        ],
    },
    {
        "name": "label coverage",
        "criterion": 2,
        # Inputs spread across your score range, so you can check all three
        # labels are actually reachable.
        "texts": [
            "Salt is used on roads to help melt ice and snow and improve traction during the winter months. When it's cold outside, water can freeze on the roads and make them very slippery, which can be dangerous for cars and people. Salt helps to melt the ice and snow by lowering the freezing point of water, which means that it can help keep the roads clear and safe to travel on. \nThere are other options for melting ice and snow on roads, such as using chemicals like calcium chloride or magnesium chloride, or using mechanical methods like plows or sand. However, salt is often the most effective and affordable option for many communities, especially when it's used in combination with other methods. \nIt's important to note that while salt can be helpful for making roads safer during the winter, it can also have negative effects on the environment and on the cars themselves. Salt can cause corrosion on metal surfaces, including cars, and it can also harm plants and animals if it washes into nearby waterways. However, despite these potential downsides, many communities continue to use salt as a way to keep roads clear and safe during the winter.",
            "They are one of the most compelling reasons to manage the livestock and food industry . Forget that they are nearly impossible to eliminate by cooking if they are in your foodstuffs . Forget the horrible , horrible way they kill . The only reason prions prolifferate is by feeding animal waste products back to your stock animals . Bovine spongiform , scrapie and CJD are all caused by eating an animals brain / spinal fluid . Surely this should not be happening ? People should have the right to trust their foodstuffs and should not be feeding dead animals back to other livestocks . That is what scares me .",
            "`What's Love Got to Do With It' tells the harrowing story of Tina Turner's life and music, and her relationship with Ike Turner. The movie shows the violence and abuse she faced, and her struggles to break free to find success on her own.Tina found the strength to stand up to Ike. In a powerful scene towards the end of the movie  Ike slips past security into Tina's dressing room with a gun and Tina finds the inner strength to face him . The movie s  Angela Bassett as Tina and Laurence Fishburne as Ike, It  features the soundtrack of Tina Turners songs performed by Bassett and the movie also has a lot of great music in it too snd its a story of pain and courage, portraying Tina Turner's resilience and showcasing her incredible talent.",
        ],
    },
    # A bad-input criterion looks like this. Uncomment and adjust if that's one
    # of your five — these are raw request bodies, sent exactly as written.
    #
    # {
    #     "name": "bad input",
    #     "criterion": 3,
    #     "bodies": [
    #         {"text": "", "creator_id": "eval_bad_empty"},
    #         {"creator_id": "eval_bad_missing"},          # no text field at all
    #         {"text": "word " * 50000, "creator_id": "eval_bad_huge"},
    #         {"text": None, "creator_id": "eval_bad_null"},
    #     ],
    # },

    # TODO: add what your remaining criteria need.
    #
    # A criterion about the appeal path can't be tested by sending text alone;
    # it needs a submission first and then an appeal against the content_id
    # that came back. You'll need to test that one by hand, or extend this file
    # and run_eval.py to do it. Saying which you did is part of the write-up.
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
