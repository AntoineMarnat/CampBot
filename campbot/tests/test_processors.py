from campbot.tests.fixtures import fix_requests, fix_dump
import os
import pytest


def test_ltag_cleaner():
    from campbot.processors import LtagCleaner

    tests = [
        (
            "L#{} | 1 | 2\nL# | 1 | 2\n\nautre texte",
            "L#{} | 1 | 2\nL# | 1 | 2\n\nautre texte"
        ), (
            "L#{} | 1 | 2\n\nL# | 1 | 2\n",
            "L#{} | 1 | 2\n\nL# | 1 | 2\n"
        ), (
            "L#{} | 1\n2 | 2\nL# | 1 | 2\n\n\nautre texte",
            "L#{} | 1<br>2 | 2\nL# | 1 | 2\n\n\nautre texte",
        ), (
            "L#{} |\n 12 | 2\nL#{} | 1 \n| 2\n",
            "L#{} | 12 | 2\nL#{} | 1 | 2\n"
        ), (
            "L#{} | 1 L# 2 | 2\nL#{} | 1 | 2\n3\n",
            "L#{} | 1 L# 2 | 2\nL#{} | 1 | 2<br>3\n"
        ), (
            "L#{} | 12 | 2\nL#{} | 1 | 2\n3\n\n4",
            "L#{} | 12 | 2\nL#{} | 1 | 2<br>3\n\n4"
        ), (
            "L#{}:1::2\n##Titre",
            "L#{}|1|2\n##Titre"
        ), (
            "L#{} |1::2",
            "L#{} |1|2"
        ), (
            "L#{}:1::2",
            "L#{}|1|2"
        ), (
            "L#{}|1:2::3||R#4||||5::::6",
            "L#{}|1:2|3|R#4|5|6"
        ), (
            "L#{} 1:2",
            "L#{} |1:2"
        ), (
            "L#{}|1::2",
            "L#{}|1|2"
        ), (
            "L#{}::1::2||3:: ::5|6| |7::8:aussi 8|9",
            "L#{}|1|2|3| |5|6| |7|8:aussi 8|9"
        ), (
            "L#~ plein ligne !:: \n| fds : \n\n| () a la fin",
            "L#~ plein ligne !:: <br>| fds : \n\n| () a la fin",
        ), (
            "L#{} || [[touche/pas|au lien]] : stp::merci ",
            "L#{} | [[touche/pas|au lien]] : stp|merci "
        ),
    ]

    numbering_postfixs = ["", "12", "+3", "+", "-25", "-+2", "+2-+1", "bis",
                          "bis2", "*5bis", "+5bis", "_", "+bis",
                          "''", "+''", "!", "2!", "+2!", "="]

    p = LtagCleaner().modify

    for postfix in numbering_postfixs:
        for markdown, expected in tests:
            markdown = markdown.format(postfix, postfix)
            expected = expected.format(postfix, postfix)

            assert p(markdown) == expected


def test_ltag_migrator():
    from campbot.processors import LtagMigrator

    tests = [
        ("L#=\nL#\nL#|L#bis\nL#~",
         "L#=\nL#1\nL#2|L#bis\nL#~"),

        ("L#=\nL#\nL#bis|L#\nL#~",
         "L#=\nL#\nL#bis|L#\nL#~"),

        ("L#\nL#+2\nL#\nL#6\nL#+2\nL#+\nL#",
         "L#1\nL#3\nL#4\nL#6\nL#8\nL#9\nL#10"),

        ("L#\nL#+1-+1\nL#-+1",
         "L#1\nL#2-3\nL#4-5"),

        ("L#-+7 | 5c\nL#",
         "L#1-8 | 5c\nL#9"),
    ]

    p = LtagMigrator().modify

    for markdown, expected in tests:
        assert p(markdown) == expected


def test_bbcode_remover():
    from campbot.processors import BBCodeRemover

    tests = [
        {
            "source": "*[Voir la discussion sur le forum.](#t158106)*",
            "expected": "*[Voir la discussion sur le forum.](https://www.camptocamp.org/forums/viewtopic.php?id=158106)*",
        },
        {
            "source": "[col][col 50 left]",
            "expected": "",
        },
        {
            "source": "x[hr]",
            "expected": "x\n----\n",
        },
        {
            "expected": "{#coucou}",
            "source": '<span id="coucou"></span>',
        },
        {
            "source": "[center]coucou[/center]",
            "expected": "<center>coucou</center>",
        },
        {
            "source": "[acr=1 goujon et 2-3 lunules]1g..3l[/acr]",
            "expected": '<abbr title="1 goujon et 2-3 lunules">1g..3l</abbr>',
        },
        {
            "source": "L#~ | coucou",
            "expected": "L#~ coucou",
        },
        {
            "source": "L# | gne\nL#~|coucou",
            "expected": "L# | gne\nL#~ coucou",
        },
        {
            "source": "L#~|   coucou\nL# | ~",
            "expected": "L#~ coucou\nL# | ~",
        },
        {
            "source": "L#~ |||| A",
            "expected": "L#~ A",
        },
        {
            "source": "un texte en [b]gras [/b]et un en [i]italique[/i] [i][/i] ",
            "expected": "un texte en **gras** et un en *italique*  ",
        },
        {
            "source": "un texte en [b][i]gras et italique[/i][/b]",
            "expected": "un texte en ***gras et italique***",
        },
        {
            "source": "[center][b]outside![/b][/center]",
            "expected": "**<center>outside!</center>**",
        },
        {
            "source": "[url=http:google.fr][i]outside![/i][/url]",
            "expected": "*[outside!](http:google.fr)*",
        },
        {
            "source": "[b]\r\ngrep!\r\n[/b]",
            "expected": "\r\n**grep!**\r\n",
        },
        {
            "source": "#c coucou ##c s",
            "expected": "# coucou ##c s",
        },
        {
            "source": "line\n####c coucou ##c s",
            "expected": "line\n#### coucou ##c s",
        },
        {
            "source": "###coucou",
            "expected": "###coucou",
        },
        {
            "source": "###C bien",
            "expected": "###C bien",
        },
        {
            "source": "[url=]http://www.zone-di-tranquillita.ch/[/url]",
            "expected": "http://www.zone-di-tranquillita.ch/ "
        },
        {
            "source": "[url]http://www.google.com[/url]",
            "expected": "http://www.google.com "
        },
        {
            "source": "[url]http://www.google.com[/url] x [url]http://www.google2.com[/url]",
            "expected": "http://www.google.com  x http://www.google2.com "
        },
        {
            "source": "[url=http://www.google.com]google[/url]",
            "expected": "[google](http://www.google.com)",
        },
        {
            "source": "[url=http://www.google.com]google[/url] et [url=http://www.google2.com]google2[/url]",
            "expected": "[google](http://www.google.com) et [google2](http://www.google2.com)"
        },
        {
            "source": "[url]http://www.google.com?a=b&c=d[/url] and [url=http://www.google.com?a=b!c]pas touche[/url]",
            "expected": "http://www.google.com?a=b&c=d  and [pas touche](http://www.google.com?a=b!c)"
        },
        {
            "source": "[url]http://www.google.com?a=b;d[/url] et [url]pas.touche.fr[/url]",
            "expected": "http://www.google.com?a=b;d  et [url]pas.touche.fr[/url]"
        },
        {
            "source": "[url]http://www.google.com?a=b&c=d[/url] x [url]http://www.google2.com?a=b&c=d[/url]",
            "expected": "http://www.google.com?a=b&c=d  x http://www.google2.com?a=b&c=d "
        },
        {
            "source": "[url=http://www.google.com?a=b&c=d]google[/url]",
            "expected": "[google](http://www.google.com?a=b&c=d)",
        },
        {
            "source": "[url=http://www.google.com?a=b&c=d]go[/url] et [url=http://www.google2.com?a=b&c=d]o[/url]",
            "expected": "[go](http://www.google.com?a=b&c=d) et [o](http://www.google2.com?a=b&c=d)"
        },
        {
            "source": "[email]dev@camptocamp.org[/email]",
            "expected": "[dev@camptocamp.org](mailto:dev@camptocamp.org)"
        },
        {
            "source": "[email=dev@camptocamp.org]email[/email]",
            "expected": "[email](mailto:dev@camptocamp.org)"
        },
        {
            "source": "[url=]http://www.zone-di-tranquillita.ch/[/url]",
            "expected": "http://www.zone-di-tranquillita.ch/ "
        },
        {
            "source": "[url]http://www.google.com?a=1&b=2[/url]",
            "expected": "http://www.google.com?a=1&b=2 "
        },
        {
            "source": "[url]http://www.google.com?a=1&b=2[/url] x [url]www.google2.com[/url]",
            "expected": "http://www.google.com?a=1&b=2  x www.google2.com "
        },
        {
            "source": "[url=http://www.google.com?a=1&b=2]google[/url]",
            "expected": "[google](http://www.google.com?a=1&b=2)",
        },
        {
            "source": "[url=http://www.google.com]google[/url] et [url=http://www.google2.com]google2[/url]",
            "expected": "[google](http://www.google.com) et [google2](http://www.google2.com)"
        },
        {
            "source": "[url]http://www.google.com?a=b&c=d[/url] and [url=http://www.google.com?a=b!c]pas touche[/url]",
            "expected": "http://www.google.com?a=b&c=d  and [pas touche](http://www.google.com?a=b!c)"
        },
        {
            "source": "[url]pas.touche.fr[/url]",
            "expected": "[url]pas.touche.fr[/url]"
        },
        {
            "source": "[url=http://www.google.com?a=b&c=d]google[/url]",
            "expected": "[google](http://www.google.com?a=b&c=d)",
        },
        {
            "source": "[url=http://www.google.com?a=b&c=d]google[/url]",
            "expected": "[google](http://www.google.com?a=b&c=d)",
        },
        {
            "source": "[sub]xx[/sub]",
            "expected": "<sub>xx</sub>",
        },
        {
            "source": "[sup]xx[/sup]",
            "expected": "<sup>xx</sup>",
        },
        {
            "source": "[s]xx[/s]",
            "expected": "<s>xx</s>",
        },
    ]

    p = BBCodeRemover().modify
    for test in tests:
        assert p(test["source"]) == test["expected"]


def test_col_u_remover():
    from campbot.processors import ColorAndUnderlineRemover

    tests = [
        {
            "source": "test [u]underlines[/u] and [color=#FFdd1E]color[/color] et [color=red]color[/color]",
            "expected": "test underlines and color et color"
        },
    ]

    p = ColorAndUnderlineRemover().modify
    for test in tests:
        assert p(test["source"]) == test["expected"]


def test_md_cleaner():
    from campbot.processors import MarkdownCleaner

    tests = [
        (
            "\n\nx\n\nx\nx\n\n\nx\n\n",
            "x\n\nx\nx\n\nx",
        ), (

            "#a\n##  b\n# c",
            "# a\n## b\n# c",
        )
    ]

    p = MarkdownCleaner().modify
    for markdown, expected in tests:
        assert p(markdown) == expected


def test_upper_fix():
    from campbot.processors.cleaners import UpperFix

    tests = [{
        "source": "## abc\n#ab\n#\n##A",
        "expected": "## Abc\n#Ab\n#\n##A",
    }, {
        "source": "|aa\nL# | aa | Aa [[routes/132|aa]] | \n a \n|a\na\n\naa",
        "expected": "|aa\nL# | Aa | Aa [[routes/132|aa]] | \n a \n|A\na\n\naa",
    }]

    p = UpperFix().modify
    for test in tests:
        assert p(test["source"]) == test["expected"]


def test_mult_sign():
    from campbot.processors.cleaners import MultiplicationSign

    tests = [

        {"source": "2*50m, 2x50 m, 2X50 m",
         "expected": "2×50 m, 2×50 m, 2×50 m"}, ]

    p = MultiplicationSign().modify
    for test in tests:
        assert p(test["source"]) == test["expected"]


def test_arabic_spaces():
    from campbot.processors.cleaners import SpaceBetweenNumberAndUnit

    tests = [
        {"source": "",
         "expected": ""},
        {"source": "prendre une corde 10-15m ou 2x50m ou 2X50m",
         "expected": "prendre une corde 10-15 m ou 2x50 m ou 2X50 m"},
        {"source": "6h, 2min! 4mn? 5m et 6km",
         "expected": "6 h, 2 min! 4 mn? 5 m et 6 km"},
        {"source": "L# | 30m |",
         "expected": "L# | 30 m |"},
        {"source": "L# |30m |",
         "expected": "L# |30 m |"},
        {"source": "L# | 30m|",
         "expected": "L# | 30 m|"},
        {"source": "6h\n",
         "expected": "6 h\n"},
        {"source": "\n6h\n",
         "expected": "\n6 h\n"},
        {"source": "\n6h",
         "expected": "\n6 h"},
        {"source": "L#6h",
         "expected": "L#6h"},
        {"source": " 6A ",
         "expected": " 6A "}, ]

    p = SpaceBetweenNumberAndUnit().modify
    for test in tests:
        assert p(test["source"]) == test["expected"]


def test_auto_replacements():
    from campbot.processors.cleaners import AutomaticReplacements

    tests = [
        ("deja", "déjà"),
        ("http://deja.com", "http://deja.com"),
        ("http://www.deja.com [www.vialsace.eu](https://www.vialsace.eu/)", "http://www.deja.com [www.vialsace.eu](https://www.vialsace.eu/)"),
        (":deja:", ":deja:"),
        ("[[route/123/fr/deja|deja]]", "[[route/123/fr/deja|déjà]]"),
        ("référencée sur www.alpes-sud.net", "référencée sur www.alpes-sud.net")
    ]

    p = AutomaticReplacements(lang="fr", comment="test", replacements=(("deja", "déjà"), ("sud", "S"))).modify

    for markdown, expected in tests:
        assert p(markdown) == expected


def test_internal_links_corrector():
    from campbot.processors.bbcode import InternalLinkCorrector

    tests = [
        {
            "source": "[[786432|patate]]",
            "expected": "[[786432|patate]]"
        },
        {
            "source": "[[/routes/786432|patate]]",
            "expected": "[[routes/786432|patate]]"
        },
        {
            "source": "[[http://www.camptocamp.org/articles/106859/fr|cotation de randonnée pédestre]]",
            "expected": "[[articles/106859/fr|cotation de randonnée pédestre]]"
        },
        {
            "source": "[[http://www.camptocamp.org/routes/173371/it/via-bartesaghi-iii-torrione|Via Bartesaghi]] ",
            "expected": "[[routes/173371/it/via-bartesaghi-iii-torrione|Via Bartesaghi]] "
        },
        {
            "source": "[[http://www.camptocamp.org/images/19796/fr/|photo]]",
            "expected": "[[images/19796/fr/|photo]]"
        },
        {
            "source": "[[http://www.camptocamp.org/routes/186949/fr/presles-approches-descentes-presles#secteur-fhara-kiri|Voir approches & descentes]]. ",
            "expected": "[[routes/186949/fr/presles-approches-descentes-presles#secteur-fhara-kiri|Voir approches & descentes]]. "
        },
    ]

    p = InternalLinkCorrector().modify

    for test in tests:
        assert p(test["source"]) == test["expected"]
