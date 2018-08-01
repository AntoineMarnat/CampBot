# coding: utf-8

from __future__ import unicode_literals

from tests.fixtures import fix_requests, fix_dump
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


def test_fixed_corrections():
    from campbot.processors.cleaners import UpperFix, MultiplicationSign, SpaceBetweenNumberAndUnit, RemoveColonInHeader

    tests = [(
        "## abc\n#ab\n#\n##A",
        "## Abc\n#Ab\n#\n##A",
    ), (
        "|aa\nL# | aa | Aa [[routes/132|aa]] | \n a \n|à\na",
        "|aa\nL# | Aa | Aa [[routes/132|aa]] | \n a \n|À\na",
    ), (
        "coucou\ncoucou\n\ncoucou",
        "Coucou\ncoucou\n\nCoucou",
    ), (
        "également\n\nà voir\n\nèh oh",
        "Également\n\nÀ voir\n\nÈh oh",
    ), (
        "2*50m, 2x50 m, 2X50 m",
        "2×50 m, 2×50 m, 2×50 m",
    ), (
        "",
        ""
    ), (
        "Prendre une corde 10-15m ou 2x50m ou 2X50m",
        "Prendre une corde 10-15 m ou 2×50 m ou 2×50 m"
    ), (
        "6h, 2min! 4mn? 5m et 6km",
        "6 h, 2 min! 4 mn? 5 m et 6 km"
    ), (
        "L# | 30m |",
        "L# | 30 m |"
    ), (
        "L# |30m |",
        "L# |30 m |"
    ), (
        "L# | 30m|",
        "L# | 30 m|"
    ), (
        "6h\n",
        "6 h\n"
    ), (
        "\n6h\n",
        "\n6 h\n"
    ), (
        "\n6h",
        "\n6 h"
    ), (
        "L#6h",
        "L#6h"
    ), (
        " 6A ",
        " 6A "
    ), (
        "1h30. Compter 1h15. ou 1h10",
        "1 h 30. Compter 1 h 15. ou 1 h 10"
    ), (
        "# X : Y :\n\n## X :\nX :\n## X #:\nY #4 X :",
        "# X : Y \n\n## X \nX :\n## X #\nY #4 X :",
    ), (
        "### Les 100 plus belles :\n",
        "### Les 100 plus belles \n"
    ), (
        "# Un [lien](https://a.com)",
        "# Un [lien](https://a.com)"
    )]

    processors = (UpperFix().modify,
                  MultiplicationSign().modify,
                  SpaceBetweenNumberAndUnit().modify,
                  RemoveColonInHeader().modify)

    for markdown, expected in tests:
        for foo in processors:
            markdown = foo(markdown)

        assert markdown == expected
        

def test_auto_replacements():
    from campbot.processors.cleaners import AutomaticReplacements

    replaced = [
        ("deja", "déjà"),
        (":deja:", ":deja:"),
        ("[[route/123/fr/deja|deja]]", "[[route/123/fr/deja|déjà]]"),
    ]

    untouched = [
        "http://deja.com",
        "http://www.deja.com [www.vialsace.eu](https://www.vialsace.eu/)",
        "[www.a.com](https://www.b.eu/) - [www.c.eu](https://www.c.eu/)",
        "référencée sur www.alpes-sud.net",
        "[[articles/226763/fr/noeud-machard#machard-tresse-img-226816-right-no-border-no-legend|Machard tressé]]",
        "[Les gites](/waypoints#a=14361%252C14328&wtyp=gite)"
    ]

    p = AutomaticReplacements(lang="fr", comment="test", replacements=(
        ("deja", "déjà"),
        ("sud", "S"),
        ("noeud", "nœud"),
        ("gite", "gîte")
    )).modify

    for markdown, expected in replaced:
        assert p(markdown) == expected

    for markdown in untouched:
        assert p(markdown) == markdown


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
