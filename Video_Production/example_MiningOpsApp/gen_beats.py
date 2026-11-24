"""gen_beats.py - single source for the film beats. Writes:
  tests/e2e/artifacts/film/beats.json   (machine contract, schema Video_Production.md 4.1 plus action and claims)
  docs/film/beat-sheet.md               (human beat sheet)
  docs/film/claims-table.md             (rule 13 claims table, one row per narrated line)
Run: C:/miniforge3/envs/py_claude/python.exe -I tests/e2e/film/gen_beats.py   (from the project root)
ASCII only. Voice text equals caption text; codes are respelled for the ear only in pronunciations.json.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CPS_S = 0.0805        # seconds of voice per character, measured on the first 5 real clips (12.4 chars/s; the self-test said 0.0747)
LOOK = 6.0            # extra quiet look time after an app landing line
LEAD, TAIL = 0.4, 1.2  # seconds before and after each clip (Video_Production.md 7.3 step 5)
D = "deck"
AS_OF = "as-of 30 Sep 2026"

BEATS = []
SCENES = []


def scene(sid, title, deck, app):
    SCENES.append({"id": sid, "title": title, "deck_slides": deck, "app": app})


def slide(bid, sid, n, text, claims, dwell=2.0):
    BEATS.append({"id": bid, "scene": sid, "kind": "slide", "source": {"slide": n}, "text": text,
                  "action": {"show": "tests/e2e/artifacts/film/slides/slide-%02d.png" % n,
                             "note": "REAL slide image, scaled to fit above the caption strip; no app action"},
                  "dwell_s": dwell, "act_s": 0.0, "role": "-", "claims": claims, "intent_or_landing": "slide"})


def app(bid, sid, page, kind, text, act_s, dwell_s, steps, claims, role="manager"):
    BEATS.append({"id": bid, "scene": sid, "kind": "app", "source": {"page": page}, "text": text,
                  "action": {"page": page, "steps": steps}, "dwell_s": dwell_s, "act_s": act_s,
                  "role": role, "claims": claims, "intent_or_landing": kind})


# selectors proven in rehearsal r2 (tests/e2e/artifacts/film/rehearsal) and in journeys N-1..N-9
NAV = lambda t: {"do": "click", "sel": 'a[title="%s"]' % t}
FIND = lambda k: {"do": "click", "sel": '.mx-name-dgFindings [role="gridcell"]:has-text("%s")' % k, "ready": ".mx-name-btnBack"}
EXPLORE = {"do": "click", "sel": ".mx-name-btnNavStart", "ready": ".mx-name-btnNavRestart", "wait_ms": 5000}
DETAILS = lambda t: {"do": "click", "sel": '.mx-name-dgNavNodes [role="row"]:has-text("%s") .mx-name-btnNavSelect' % t, "ready": ".mx-name-txtNavSelTitle", "wait_ms": 3500}
SCROLL = lambda sel, block="center": {"do": "scroll", "sel": sel, "block": block}
GRAPHBOX = '[class*="mx-name-ngNav"]:visible'
TAB = lambda t: {"do": "click", "sel": '.mx-name-tcCompliance [role="tab"]:has-text("%s")' % t}

# ------------------------------------------------------------------------------------------ A
scene("A", "Opening and the problem", "1, 4, 5, 6 (slides 2, 3 and 7 skipped: agenda, chapter title, competitor field with unverified characterisations)", "none")
slide("A01", "A", 1, "Welcome. This film walks through a real working app, built on a knowledge graph of synthetic data that mirrors Iluka's value chain. Each question appears first as a slide, then live in the app.",
      [["slide 1 title 'Connecting Iluka'; 'synthetic data that mirrors Iluka's value chain'", "deck slide 1 notes"]])
slide("A03", "A", 4, "Iluka's value chain runs from exploration to the port, and every stage keeps its own slice of the truth in a different system. Nineteen source systems in the demo graph, and none can answer a cross-stage question alone.",
      [["nineteen source systems in the demo graph", "deck slide 4 ('19 source systems in the demo graph')"], ["none can answer a cross-stage question alone", "deck slide 4"]])
slide("A04", "A", 5, "What we heard is that Iluka's plan already names the destination: a shared vocabulary on open standards. The graph is how that strategy becomes something you can actually query.",
      [["plan names a shared vocabulary on open standards", "deck slide 5 headline and notes"]])
slide("A05", "A", 6, "Every useful question crosses four or more systems. Today a person exports from each one, joins the results in a spreadsheet, and hopes the names match. With a graph, it's one query.",
      [["four or more systems", "deck slide 6 title"], ["export, spreadsheet join, names match; with a graph one query", "deck slide 6 footer line"]])

# ------------------------------------------------------------------------------------------ B
scene("B", "Approach and architecture (brief)", "9, 12, 23 (10, 17 and the rest of 8-22 skipped for length)", "none")
slide("B01", "B", 9, "The approach is one stack. Graph Studio builds and governs the model, Graph Lakehouse serves it, and a SHACL gate guards the door. The model is plain W3C standards, so no vendor owns the meaning.",
      [["Graph Studio builds and governs, Graph Lakehouse serves, SHACL guards the door", "deck slide 9 subtitle"], ["plain W3C standards, no vendor owns the meaning", "deck slide 9 footer"]])
slide("B03", "B", 12, "Lineage is the backbone. Every lot points at the lot it came from, so a customer claim can be walked back to the ore block. The demo has one thousand nine hundred sixty-one material lots, joined by one thousand four hundred ninety-eight links.",
      [["1,961 material lots", "deck slide 12"], ["1,498 derivedFromLot links", "deck slide 12"]])
slide("B05", "B", 23, "For this demo, the ontology and the data are both Turtle files: thirty-five data files, two hundred eleven thousand nine hundred thirty-two triples. Live systems would feed the same model by direct load or virtualisation.",
      [["35 Turtle files, 211,932 triples", "deck slide 23 step 01"], ["live systems fed by direct load or virtualisation", "deck slide 23 footer and slide 9"]])

# ------------------------------------------------------------------------------------------ C
scene("C", "The app: the Findings feed", "none (bridge from slide 23)", "Findings")
app("C01", "C", "Findings", "intent", "Now the app. I'm signed in as a manager, and I'll open Findings.", 3.5, 0.5,
    [NAV("Findings"), {"do": "wait_for", "sel": '.mx-name-dgFindings [role="gridcell"]'}],
    [["signed in as a manager", "login as demo user manager (off camera); nav shows Cases landing for manager (rehearsal 01-landing)"]])
app("C02", "C", "Findings", "landing", "Eight detectors run against the graph, and each reports one finding here, from critical down to low. Everything is as of the thirtieth of September, twenty twenty-six, shown at the top right.", 1.0, 3.0,
    [{"do": "spot", "sel": ".mx-name-dgFindings"}, {"do": "park", "note": "cursor rests near the As of badge top right"}],
    [["eight detectors", "Findings subtitle '8 detectors, refreshed ... for as-of 30 Sep 2026' (explore1 findings)"], ["severity from critical to low", "grid rows: Critical x1, High x3, Medium x2, Low x2"], ["as of 30 September 2026 at the top right", "badge 'As of 30 Sep 2026' (02-findings-list.png)"]])
app("C03", "C", "Findings", "landing", "A word on names. In the deck the questions are numbered one to eight. The app labels the detectors S one to S eight, in a different order, so I'll name each finding as we go.", 1.0, 3.5,
    [{"do": "spot", "sel": ".mx-name-dgFindings [role=\"columnheader\"]:has-text(\"Detector\")"}],
    [["detectors labelled S1 to S8 in another order", "Detector column S4,S6,S8,S3,S1,S5,S7,S2 (explore1 findings rows)"]])

# ------------------------------------------------------------------------------------------ Q1
scene("Q1", "Question 1: the Castellon claim (deck Q1 = app detector S3, finding SHP-ZR-024)", "26, 27", "Finding_Detail, Case_View, Trace_Overview, navigator on Finding_Detail")
slide("Q1S1", "Q1", 26, "Question one: why did Castellon raise a quality claim? Seven zircon lots broke the iron oxide limit in the Castellon contract, and they all came off one separator, MS-03, whose planned maintenance was overdue.",
      [["seven zircon lots over the iron oxide (Fe2O3) limit, Castellon contract", "deck slide 26 notes"], ["one separator MS-03, maintenance overdue", "deck slide 26 table and notes"]])
app("Q1A1", "Q1", "Finding_Detail", "intent", "In the app, that's the high severity finding on shipment SHP-ZR-024. Let's open it.", 4.0, 0.5,
    [NAV("Findings"), FIND("SHP-ZR-024")],
    [["high severity", "Findings row High; Finding_Detail severity chip High (03-S3-finding)"]])
app("Q1A2", "Q1", "Finding_Detail", "landing", "The evidence is the same seven lots, each above the point one iron oxide limit, all from separator MS-03, whose work order was due on the fifteenth of June and finished on the first of July.", 1.0, 3.5,
    [{"do": "spot", "sel": ".mx-name-dgS3Ev"}],
    [["same seven lots, readings above 0.1 limit", "Evidence grid: 7 rows, Fe2O3 0.13-0.169, Spec max 0.1 (fd-S3 text)"], ["separator MS-03", "Equipment column / header 'Narngulu Rare Earth Roll Magnetic Separator MS-03'"], ["work order due 15 June, finished 1 July", "WO due 15 Jun 2026, WO completed 1 Jul 2026 on every row"]])
app("Q1A3", "Q1", "Finding_Detail", "landing", "Further down, the separator's magnetic field strength by day: near one on the fifteenth of June, falling to point seven one seven by the thirtieth. On the first of July, when the work order was done, it's back to point nine eight nine.", 6.0, 3.0,
    [SCROLL(".mx-name-dgS3Ctx [role=\"row\"]:has-text(\"30 Jun 2026\")", "center")],
    [["starts near one on 15 June (1.004)", "context grid QA-S3b first row 15 Jun 2026 1.004"], ["0.717 on 30 June", "row 30 Jun 2026 0.717"], ["0.989 on 1 July, the day the work order completed", "row 1 Jul 2026 0.989; WO completed 1 Jul 2026"]])
app("Q1A4", "Q1", "Case_View", "intent", "Every finding can become a case, and this one already has one. Go to case.", 4.0, 0.5,
    [SCROLL(".mx-name-btnGoToCase", "start"), {"do": "click", "sel": ".mx-name-btnGoToCase", "ready": ".mx-name-txtTitle"}],
    [["this finding already has a case", "Case card 'Case state Open'; Go to case button present (03-S3-finding)"]])
app("Q1A5", "Q1", "Case_View", "landing", "The case is open, severity high, owned by hse, with a due date of the thirty-first of December. Its one task is already done.", 1.0, 3.5,
    [{"do": "spot", "sel": ".mx-name-ctnHeaderCard"}],
    [["case open", "status badge Open (05-S3-case-view)"], ["severity high", "badge High"], ["owner hse", "OWNER hse"], ["due 31 December", "CASE DUE 31 Dec 2026"], ["one task, done", "Tasks grid 1 row, status Done"]])
slide("Q1S2", "Q1", 27, "And which ore blocks sit behind that claim? One property path walks from the shipment back through four steps to the mine. Fourteen run-of-mine lots, from only four ore blocks.",
      [["fourteen run-of-mine lots, four ore blocks", "deck slide 27 result (14 ROM lots) and subtitle"]])
app("Q1A6", "Q1", "Trace_Overview", "intent", "Back on the finding, Trace this shipment does the same walk in the app.", 6.0, 0.5,
    [NAV("Findings"), FIND("SHP-ZR-024"), {"do": "click", "sel": ".mx-name-btnTraceShipment", "ready": '.mx-name-dgBack [role="gridcell"]', "timeout_ms": 90000}],
    [["Trace this shipment opens the back trace", "journey J-05 TR-S3link; rehearsal 06-S3-trace PASS"]])
app("Q1A7", "Q1", "Trace_Overview", "landing", "Seven lots shipped, fourteen run-of-mine lots, four ore blocks, all at Cataby. The blocks are CAT-N-021, CAT-N-022, CAT-S-021 and CAT-S-022, mined between the twenty-first and twenty-seventh of June.", 1.0, 4.0,
    [{"do": "spot", "sel": ".mx-name-dgBack"}],
    [["7 lots shipped, 14 ROM lots, 4 ore blocks, Cataby", "chips '7 lots shipped to 14 ROM lots to 4 ore blocks, Cataby' (06-S3-trace)"], ["blocks CAT-N-021, CAT-N-022, CAT-S-021, CAT-S-022", "grid rows"], ["21 to 27 June", "footer '4 ore blocks, 14 ROM lots, ROM dates 21 Jun 2026 - 27 Jun 2026'"]])
app("Q1A8", "Q1", "Finding_Detail", "intent", "One more tool is on the finding page: the graph navigator. Nothing loads until you ask, so I'll ask.", 6.0, 0.5,
    [NAV("Findings"), FIND("SHP-ZR-024"), SCROLL(".mx-name-btnNavStart", "center"), EXPLORE],
    [["nothing loads until you ask", "card text 'Nothing is loaded until you ask.' (S2 finding text)"]])
app("Q1A9", "Q1", "Finding_Detail", "landing", "One query, and the finding's own records appear: twenty-four records and twenty-two links. Notice two clusters.", 3.0, 3.0,
    [SCROLL(GRAPHBOX, "center"), {"do": "zoom", "sel": GRAPHBOX}],
    [["24 records and 22 links", "counts line '24 records and 22 links shown' (journey N-1; nav-s3-1b-graph)"], ["two clusters", "nav-s3-1b-graph-1600.png: left hub shipment, right hub equipment"]])
app("Q1A10", "Q1", "Finding_Detail", "landing", "On the left, the product trail: the shipment, its seven zircon lots, the concentrate lots they came from, and the Castellon contract. On the right, the machine trail: the separator, its work orders and the Narngulu site.", 5.0, 3.0,
    [{"do": "glide", "from": "left cluster", "to": "right cluster", "sel": GRAPHBOX, "note": "cursor glides over the left hub, then the right hub"}],
    [["left: shipment, 7 zircon lots, concentrate lots, contract", "link-type filter: ships lot (7), derived from lot (7), under contract (1)"], ["right: separator, work orders, Narngulu site", "link-type filter: work order for (6), located at site (1); hub eq_nar_ms03 (nav-s3-1b-graph)"]])
app("Q1A11", "Q1", "Finding_Detail", "intent", "Select the shipment, and the app offers a detector question: which other shipments share these lots?", 5.0, 0.5,
    [SCROLL(".mx-name-dgNavNodes", "start"), DETAILS("SHP-ZR-024")],
    [["offers 'Which other shipments share its lots?'", "panel button 'Which other shipments share its lots? (S3)' (nav-s3-3-preset)"]])
app("Q1A12", "Q1", "Finding_Detail", "landing", "One more query, and three more shipments join the picture, twenty-seven records in all. So the problem may not stop at Castellon.", 14.0, 3.0,
    [{"do": "click", "sel": ".mx-name-btnNavPresetS3", "wait_ms": 12000}, SCROLL(GRAPHBOX, "center")],
    [["27 records in all", "counts '27 records and 25 links shown' (rehearse-s3b)"], ["three more shipments", "SHP-SR-027 (page 1), SHP-SR-025 and SHP-RT-056 (page 2) (rehearse-s3b; journey N-1)"]])

# ------------------------------------------------------------------------------------------ Q2
scene("Q2", "Question 2: synthetic rutile below spec (deck Q2 = app detector S1, finding Capel Kiln Line SR2 10 Jul 2026)", "28", "Finding_Detail with the S1 preset and kiln comparison")
slide("Q2S1", "Q2", 28, "Question two: why did synthetic rutile fall below spec? A low-grade ilmenite block and a kiln temperature excursion, together. Kiln SR1 got the same feed and stayed in spec at ninety point five percent; SR2 missed at eighty-nine point four.",
      [["two causes together: low-grade ilmenite block, kiln temperature excursion", "deck slide 28 subtitle"], ["SR1 ninety point five percent, SR2 eighty-nine point four", "deck slide 28 callout '90.5% vs 89.4% TiO2'"], ["SR1 same feed, no excursion, met spec", "deck slide 28 text"]])
app("Q2A1", "Q2", "Finding_Detail", "intent", "In the app, it's a medium finding on Capel Kiln Line SR2, tenth of July.", 4.0, 0.5,
    [NAV("Findings"), FIND("Capel Kiln Line SR2 10 Jul 2026")],
    [["medium severity, Capel Kiln Line SR2, 10 July", "Findings row Medium, 'Capel Kiln Line SR2 10 Jul 2026' (explore1)"]])
app("Q2A2", "Q2", "Finding_Detail", "landing", "Three rutile lots below the ninety percent spec, all fed from block CAT-S-024, on days when the kiln peaked above twelve hundred degrees.", 1.0, 3.5,
    [{"do": "spot", "sel": ".mx-name-dgS1Ev"}],
    [["three lots below 90 percent spec", "evidence rows SR TiO2 89.574, 89.29, 89.455; Spec min 90 (fd-S1 text)"], ["source block CAT-S-024", "Source block column CAT-S-024"], ["kiln peak above 1200 degrees", "Max temp C 1213.1, 1214.2, 1206.4"]])
app("Q2A3", "Q2", "Finding_Detail", "landing", "The context table compares the kilns on low-feed days. SR2, on excursion days above eleven hundred eighty degrees, averaged eighty-nine point four four over three days. SR1, with no excursion, averaged ninety point five over four.", 6.0, 3.0,
    [SCROLL(".mx-name-dgS1Ctx", "start")],
    [["SR2 excursion above 1180 degrees: 89.44 over 3 days", "context S1b row 'Capel Kiln Line SR2 Low feed TiO2 Excursion > 1180 degC 3 89.43966667'"], ["SR1 no excursion: 90.5 over 4 days", "context row 'Capel Kiln Line SR1 Low feed TiO2 Normal 4 90.49775'"]])
app("Q2A4", "Q2", "Finding_Detail", "intent", "Now the graph navigator. Explore, select the first rutile lot, and ask the S1 question.", 12.0, 0.5,
    [SCROLL(".mx-name-btnNavStart", "center"), EXPLORE, SCROLL(".mx-name-dgNavNodes", "start"), DETAILS("lot_SR_SR2_20260710")],
    [["S1 question is offered on the SR lot", "panel 'Trace back to ore block and grade (S1)' (journey N-2)"]])
app("Q2A5", "Q2", "Finding_Detail", "landing", "Two queries bring in the ore block with its model grades, and the other kiln's lots. The banner sums it up: SR2, eighty-nine point four four over three days above eleven hundred eighty degrees; SR1, ninety point five over four days at or below.", 16.0, 4.0,
    [{"do": "click", "sel": ".mx-name-btnNavPresetS1", "wait_ms": 14000}, SCROLL(".mx-name-ctnNavStatus", "start"), {"do": "spot", "sel": ".mx-name-ctnNavStatus"}],
    [["two queries", "log lines Graph query QN-4 and QN-4b exactly once each (journey N-2)"], ["ore block with model grades", "details of CAT-S-024: model grades 7.84 percent and 51.6 percent (journey N-2)"], ["banner: SR2 89.44 over 3 days above 1180; SR1 90.50 over 4 days at or below", "status banner (rehearse.js step 13): 'SR2 averaged 89.44 % ... 3 days above 1180 degC; SR1 averaged 90.50 % ... 4 days at or below 1180 degC'"]])

# ------------------------------------------------------------------------------------------ Q3
scene("Q3", "Question 3: grade reconciliation (deck Q3 = app detector S2, finding CAT-N-018)", "29", "Finding_Detail")
slide("Q3S1", "Q3", 29, "Question three: is the mine delivering what the model promised? Only one ore block is more than fifteen percent off. On CAT-N-018, the delivered heavy mineral is twenty point six percent under the block model.",
      [["only one block outside fifteen percent tolerance", "deck slide 29 subtitle and result (1 row)"], ["minus twenty point six percent on CAT-N-018", "deck slide 29 callout '-20.6%'"]])
app("Q3A1", "Q3", "Finding_Detail", "intent", "In the app, that's a low severity finding at Cataby.", 4.0, 0.5,
    [NAV("Findings"), FIND("CAT-N-018")],
    [["low severity, Cataby", "Findings row Low, site Cataby (explore1)"]])
app("Q3A2", "Q3", "Finding_Detail", "landing", "One evidence row: the block model says nine point six percent heavy mineral, the run-of-mine lots delivered seven point six two seven, a variance of about minus twenty point six percent, over four lots from the eighth to the eleventh of June.", 1.0, 4.0,
    [{"do": "spot", "sel": ".mx-name-dgS2Ev"}],
    [["model 9.6, actual 7.627", "evidence row 'CAT-N-018 9.6 7.627' (fd-S2)"], ["variance about minus 20.6 percent", "evidence row variance -20.55208333 (rounds to -20.6; deck slide 29 shows -20.6)"], ["four lots, 8 to 11 June", "ROM lots 4, First lot 8 Jun 2026, Last lot 11 Jun 2026"]])

# ------------------------------------------------------------------------------------------ Q4
scene("Q4", "Question 4: Balranald steering (deck Q4 = app detector S5, finding BAL-RUM-03)", "30", "Finding_Detail")
slide("Q4S1", "Q4", 30, "Question four: is Balranald steering off-plan? Six survey stations went beyond the one point five metre tolerance, drifting towards the ore boundary, and the runs that followed show the dilution: twelve above fifteen percent.",
      [["six stations beyond 1.5 m tolerance, drifting towards the ore boundary", "deck slide 30 table (6 rows, TOL 1.5)"], ["twelve runs above fifteen percent dilution", "deck slide 30 callout '12 runs above 15% dilution'"]])
app("Q4A1", "Q4", "Finding_Detail", "intent", "In the app, it's a medium finding on borehole BAL-RUM-03 at Balranald.", 4.0, 0.5,
    [NAV("Findings"), FIND("BAL-RUM-03")],
    [["medium severity, BAL-RUM-03, Balranald", "Findings row Medium Balranald (explore1)"]])
app("Q4A2", "Q4", "Finding_Detail", "landing", "A deviation event, already closed, with its corrective action: a steering correction applied from five hundred ten metres, and the trajectory back within tolerance by five hundred seventy.", 1.0, 3.5,
    [{"do": "spot", "sel": "text=Deviation event and corrective action"}],
    [["event closed", "STATUS Closed (fd-S5-1440-top.png)"], ["correction from 510 m, back within tolerance by 570 m", "CORRECTIVE ACTION 'Steering correction applied from MD 510; trajectory recovered within tolerance by MD 570'"]])
app("Q4A3", "Q4", "Finding_Detail", "landing", "Six survey stations beyond tolerance. The worst is a deviation of three point two metres at four hundred eighty metres depth, only point two metres from the ore boundary.", 4.0, 3.5,
    [SCROLL(".mx-name-dgS5St", "start")],
    [["six stations beyond tolerance", "grid rows 6 (fd-S5 text 'Currently showing 1 to 6 of 6')"], ["worst: 3.2 m at 480 m depth, 0.2 m from the ore boundary", "row 7 May 2026: MD 480, Deviation 3.2, Tolerance 1.5, Distance 0.2"]])
app("Q4A4", "Q4", "Finding_Detail", "landing", "Further down, the mining runs above the dilution threshold, each with its date. Twelve runs, peaking at about twenty-four percent.", 4.0, 3.0,
    [SCROLL(".mx-name-dgS5Run", "start")],
    [["twelve runs above the threshold", "Finding summary '12 runs above 15 pct dilution (max 23.59, Jul)'; deck slide 30 callout"], ["peak about twenty-four percent", "max 23.59 (rounds to 24; deck slide 30 'peak 24%')"]])

# ------------------------------------------------------------------------------------------ Q5
scene("Q5", "Question 5: third-party feed and reagent (deck Q5 = app detector S7, finding TP_002, simulated data)", "31", "Finding_Detail")
slide("Q5S1", "Q5", 31, "Question five: is third-party feed costing more reagent? Third-party lot TP_002 needs forty-eight percent more extractant than our own concentrate, with lower extraction efficiency. The refinery data is simulated.",
      [["plus forty-eight percent extractant on TP_002, lower efficiency", "deck slide 31 callout '+48% extractant'"], ["refinery data simulated", "deck slide 31 subtitle and notes"]])
app("Q5A1", "Q5", "Finding_Detail", "intent", "In the app, a low severity finding at Eneabba, tagged Simulated.", 4.0, 0.5,
    [NAV("Findings"), FIND("TP_002")],
    [["low severity, Eneabba, Simulated tag", "Findings row Low Eneabba; Finding_Detail chip Simulated (18-S7-finding.png)"]])
app("Q5A2", "Q5", "Finding_Detail", "landing", "The caveat stays on screen: a Simulated tag. TP_002 used five point eight five kilograms of extractant per tonne against three point nine four for our own concentrate, and extracted ninety point eight percent against ninety-six point five.", 1.0, 4.0,
    [{"do": "spot", "sel": ".mx-name-dgS7Ev"}],
    [["Simulated tag and 'Refinery records are simulated'", "18-S7-finding.png"], ["5.85 kg/t against 3.94", "rows TP_002 5.85285714; Own monazite concentrate 3.94363636"], ["90.8 percent against 96.5", "rows 90.83285714 and 96.53409091"]])

# ------------------------------------------------------------------------------------------ Q6
scene("Q6", "Question 6: monazite radiation (deck Q6 = app detector S4, finding MONAZITE_NAR_20260819) and Compliance", "32", "Finding_Detail, Compliance (Radiation readings)")
slide("Q6S1", "Q6", 32, "Question six: which consignment breached the radiation limit? One monazite haul measured seven point four microsieverts per hour against a limit of five. The limit is a synthetic demo value, held on the licence as data.",
      [["7.4 against a limit of 5 microsieverts per hour", "deck slide 32 callout"], ["limit is synthetic, held on the licence as data", "deck slide 32 callout and notes"]])
app("Q6A1", "Q6", "Finding_Detail", "intent", "In the app, it's the only critical finding, and it has no case yet.", 4.0, 0.5,
    [NAV("Findings"), FIND("MONAZITE_NAR_20260819")],
    [["only critical finding", "Findings: Critical x1 (explore1)"], ["no case yet", "Case state 'No case'; button 'Open case' (fd-S4)"]])
app("Q6A2", "Q6", "Finding_Detail", "landing", "The lot, MONAZITE_NAR_20260819: seven point four against a limit of five, three hundred twelve becquerel per gram, hauled from Narngulu to Eneabba and measured by Grace Dawson.", 1.0, 4.0,
    [{"do": "spot", "sel": ".mx-name-dgS4Ev"}],
    [["7.4 against limit 5", "evidence Dose 7.4, Limit 5"], ["312 becquerel per gram", "Activity Bq/g 312"], ["Narngulu to Eneabba, measured by Grace Dawson", "From site Narngulu, To site Eneabba, Measured by Grace Dawson"]])
app("Q6A3", "Q6", "Compliance", "intent", "The Compliance page shows the same fact from the other side.", 6.0, 0.5,
    [NAV("Compliance"), {"do": "wait_for", "sel": '.mx-name-dgLapses [role="gridcell"]'}, TAB("Radiation")],
    [["Compliance shows the same fact", "Radiation readings tab (20-S4-compliance-radiation.png)"]])
app("Q6A4", "Q6", "Compliance", "landing", "One hundred eighty-three radiation readings, exactly one over its limit: RM00138, flagged Over limit. The page also notes the dose limit is synthetic, and only two of six licences carry one.", 9.0, 3.0,
    [{"do": "combobox", "widget": "cmbSite", "match": "Narngulu"}, {"do": "fill", "widget": "dpFrom", "value": "19 Aug 2026"}, {"do": "fill", "widget": "dpTo", "value": "19 Aug 2026"}, {"do": "click", "sel": ".mx-name-txtDateHint"}, {"do": "spot", "sel": ".mx-name-dgRadiation"}],
    [["183 readings, exactly one over its limit", "'183 radiation readings, 1 over their limit' (journey J-04)"], ["RM00138 flagged Over limit", "row RM00138 7.40 5.00 Over limit (21-S4-compliance-radiation-filter.png)"], ["limit synthetic, only 2 of 6 licences carry one", "page note 'The 5.0 uSv/h dose limit is synthetic; only 2 of 6 licences carry one.'"]])

# ------------------------------------------------------------------------------------------ Q7
scene("Q7", "Question 7: certification (deck Q7 = app detector S6, finding INC00027)", "33", "Finding_Detail with the S6 preset, Compliance (Lapsed certifications)")
slide("Q7S1", "Q7", 33, "Question seven: who operated without a valid certification? Amelia Sinclair worked on Capel Reduction Kiln SR1 after her kiln operation certificate expired on the thirty-first of May. The follow-up counts sixty shifts like that.",
      [["Amelia Sinclair, Capel Reduction Kiln SR1, certificate expired 31 May", "deck slide 33 table"], ["sixty shifts", "deck slide 33 callout and notes"]])
app("Q7A1", "Q7", "Finding_Detail", "intent", "In the app, that's incident INC00027, a high severity finding at Capel.", 4.0, 0.5,
    [NAV("Findings"), FIND("INC00027")],
    [["INC00027 high severity, Capel", "Findings row High, site Capel (explore1)"]])
app("Q7A2", "Q7", "Finding_Detail", "landing", "The evidence row names the person, the equipment, the competency, Kiln Operation, and the expiry, the thirty-first of May. The context table counts sixty uncertified shifts, from the fourth of June to the twenty-seventh of September.", 3.0, 3.5,
    [{"do": "spot", "sel": ".mx-name-dgS6Ev"}, SCROLL(".mx-name-dgS6Ctx", "start")],
    [["person, equipment, Kiln Operation, expiry 31 May", "evidence row (fd-S6)"], ["sixty uncertified shifts", "context S6b 'Uncertified shifts 60'"], ["4 June to 27 September", "First shift 4 Jun 2026, Last shift 27 Sep 2026"]])
app("Q7A3", "Q7", "Finding_Detail", "intent", "In the navigator, I'll select the incident and ask the S6 question.", 10.0, 0.5,
    [SCROLL(".mx-name-btnNavStart", "center"), EXPLORE, SCROLL(".mx-name-dgNavNodes", "start"), DETAILS("INC00027")],
    [["S6 question offered on the incident", "journey N-3 step 3"]])
app("Q7A4", "Q7", "Finding_Detail", "landing", "The lapsed operator and her equipment join the picture: eleven records, eleven links. Six planned work orders hang off the kiln, and she's listed with her expired certificate.", 14.0, 4.0,
    [{"do": "click", "sel": ".mx-name-btnNavPresetS6", "wait_ms": 12000}, SCROLL(GRAPHBOX, "center")],
    [["eleven records, eleven links", "counts '11 records and 11 links shown' (rehearse.js step 23)"], ["kiln has six work orders", "link-type filter 'work order for (6)'; titles 'Planned inspection and service'"], ["person listed with expired certificate", "row 'Amelia Sinclair Person ... Certificate for Kiln Operation expired 31 May 2026.'"]])
app("Q7A5", "Q7", "Compliance", "landing", "The Compliance page lists all six people with a lapsed certificate. Amelia Sinclair is one of them.", 6.0, 3.0,
    [NAV("Compliance"), {"do": "wait_for", "sel": '.mx-name-dgLapses [role="gridcell"]'}, {"do": "spot", "sel": ".mx-name-dgLapses"}],
    [["six people with a lapsed certificate", "page text '6 people hold an expired certificate with no valid replacement' (24-S6-compliance-lapsed)"], ["Amelia Sinclair among them", "grid row Amelia Sinclair"]])

# ------------------------------------------------------------------------------------------ Q8
scene("Q8", "Question 8: rehabilitation (deck Q8 = app detector S8, finding OBL-007), Compliance and Sites", "34", "Finding_Detail, Compliance (Obligations), Site_View Cataby")
slide("Q8S1", "Q8", 34, "Question eight: which rehabilitation obligations are overdue? Just one: area RA-CAT-07 at Cataby, due on the thirtieth of June, with seventeen hectares still short of its forty-five hectare target.",
      [["one overdue obligation, RA-CAT-07 at Cataby, due 30 June", "deck slide 34 table"], ["seventeen hectares short of a forty-five hectare target", "deck slide 34 callout and table"]])
app("Q8A1", "Q8", "Finding_Detail", "intent", "In the app, a high severity finding at Cataby: obligation OBL-007.", 4.0, 0.5,
    [NAV("Findings"), FIND("OBL-007")],
    [["high severity, Cataby, OBL-007", "Findings row High Cataby (explore1)"]])
app("Q8A2", "Q8", "Finding_Detail", "landing", "Target forty-five hectares, rehabilitated twenty-eight, shortfall seventeen. The accountable owner, read from the graph, is Amelia Prescott.", 1.0, 4.0,
    [{"do": "spot", "sel": ".mx-name-dgS8Ev"}],
    [["45 target, 28 rehabilitated, 17 shortfall", "evidence row (fd-S8)"], ["owner Amelia Prescott, read from the graph", "column 'Obligation owner (graph)' Amelia Prescott"]])
app("Q8A3", "Q8", "Compliance", "intent", "Compliance lists every obligation.", 6.0, 0.5,
    [NAV("Compliance"), {"do": "wait_for", "sel": '.mx-name-dgLapses [role="gridcell"]'}, TAB("Obligations")],
    [["Compliance lists obligations", "Obligations tab (26-S8-compliance-obligations.png)"]])
app("Q8A4", "Q8", "Compliance", "landing", "Nineteen obligations: twelve completed, seven open, and one of those is overdue. That's OBL-007, highlighted and flagged Overdue.", 4.0, 3.5,
    [{"do": "spot", "sel": ".mx-name-dgObligations [role=\"row\"]:has-text(\"OBL-007\")"}],
    [["19 obligations, 12 completed, 7 open, 1 overdue", "'19 obligations, any due date: 12 completed, 7 open of which 1 overdue at 30 Sep 2026'"], ["OBL-007 highlighted, Overdue", "row OBL-007 red, 'Open - Overdue', badge Overdue"]])
app("Q8A5", "Q8", "Site_View", "landing", "And the Sites page: open Cataby, and the same obligation is listed under its open cases.", 8.0, 3.0,
    [NAV("Sites"), {"do": "click", "sel": '.mx-name-galSites .mx-name-ctnSiteCard:has-text("Cataby")', "ready": '.mx-name-dgUnits [role="gridcell"]'}, {"do": "spot", "sel": ".mx-name-dgCases"}],
    [["Cataby lists OBL-007 under open cases", "Site_View 'Open cases at Cataby ... OBL-007' (27-sites-cataby.png; journey J-06)"]])

# ------------------------------------------------------------------------------------------ R
scene("R", "Results, roles and when the graph is down", "35", "Case_View navigator (manager, then viewer), graph-down on Finding_Detail")
slide("R01", "R", 35, "That's all eight questions answered. Thirty-five datasets, two hundred eleven thousand nine hundred thirty-two triples, eight scenarios confirmed end to end with no false positives. The data is synthetic, and the refinery records are simulated.",
      [["35 datasets, 211,932 triples", "deck slide 35 title and subtitle"], ["eight scenarios confirmed, no false positives", "deck slide 35 subtitle"], ["data synthetic, refinery simulated", "deck slide 35 notes"]])
app("R02", "R", "Case_View", "intent", "Roles matter. As a manager, I'll open the case and use the navigator on the contract.", 14.0, 0.5,
    [NAV("Findings"), FIND("SHP-ZR-024"), {"do": "click", "sel": ".mx-name-btnGoToCase", "ready": ".mx-name-txtTitle"}, SCROLL(".mx-name-btnNavStart", "center"), EXPLORE, SCROLL(".mx-name-dgNavNodes", "start"), DETAILS("Contract ZR_CASTELLON")],
    [["manager role", "login as manager"]])
app("R03", "R", "Case_View", "landing", "Selecting a record offers Add a task about this. It opens a popup prefilled with the record. I'll cancel, so nothing is saved.", 8.0, 2.5,
    [{"do": "click", "sel": ".mx-name-btnNavAddTask", "ready": ".mx-name-taDesc"}, {"do": "spot", "sel": ".mx-name-taDesc"}, {"do": "click", "sel": ".mx-name-btnTaskCancel", "note": "Cancel, never Save"}],
    [["offers Add a task about this", "button btnNavAddTask (N-2; rehearse step 10)"], ["popup prefilled with the record", "'Look into Contract ZR_CASTELLON (Sales contract, record contract_zr_castellon)' (popup-open.png)"], ["cancelled, nothing saved", "Cancel button used; journey N-2 data check Task count unchanged"]])
app("R04", "R", "Case_View", "intent", "Now the same case as a viewer. Same graph, same details.", 14.0, 0.5,
    [{"do": "session", "user": "viewer", "note": "second segment: sign-in off camera, capture starts on the signed-in page"}, NAV("Findings"), FIND("SHP-ZR-024"), {"do": "click", "sel": ".mx-name-btnGoToCase", "ready": ".mx-name-txtTitle"}, SCROLL(".mx-name-btnNavStart", "center"), EXPLORE, SCROLL(".mx-name-dgNavNodes", "start"), DETAILS("Contract ZR_CASTELLON")],
    [["viewer role, same case", "login as viewer; rehearsal viewer r2 PASS"]], role="viewer")
app("R05", "R", "Case_View", "landing", "There's no Add a task about this. It isn't only hidden: the server refuses it for viewers and operators.", 1.0, 4.0,
    [{"do": "spot", "sel": ".mx-name-dvNavSel"}],
    [["no Add a task about this for the viewer", "viewer rehearsal: 'Add a task button count: 0' (r2-1600-viewer 03)"], ["server refuses it for viewers and operators", "N-8 server half probe-n8.js PASS 53: ACT_Nav_AddTask refused for Viewer and Operator (analysis/tools/stage6/tmp/n99/REPORT.md); not visible on screen"]], role="viewer")
app("R06", "R", "Finding_Detail", "intent", "One last thing: what if the graph goes down? I'll explore a finding and then take the graph away.", 12.0, 0.5,
    [{"do": "session", "user": "manager", "note": "app started with GRAPH_BASE_URL=http://127.0.0.1:18080 and graph-proxy.js up; proxy flipped down by GET http://127.0.0.1:18081/down at the moment of the click"}, NAV("Findings"), FIND("SHP-ZR-024"), EXPLORE, {"do": "proxy", "state": "down"}],
    [["the graph is taken away for this demo", "rehearse-down.js: proxy control /down (rehearsed 2026-11-15)"]])
app("R07", "R", "Finding_Detail", "landing", "The app says so plainly: could not load the details, the graph server cannot be reached. The connections already shown are unchanged.", 9.0, 4.0,
    [DETAILS("Contract ZR_CASTELLON"), SCROLL(".mx-name-ctnNavStatus", "center"), {"do": "spot", "sel": ".mx-name-ctnNavStatus"}, {"do": "proxy", "state": "up"}],
    [["could not load the details, graph server cannot be reached", "status 'Could not load the details (query QN-2): Graph query QN-2 failed: the graph server cannot be reached; check graph.base_url and the network.' (down-details-1600.png)"], ["connections already shown unchanged", "counts line stays '24 records and 22 links shown' (rehearse-down.js)"]])

# ------------------------------------------------------------------------------------------ P
scene("P", "The path forward and close", "37, 40, 43, 46, 47 (slides 36, 38, 39, 41, 42, 44, 45 and the appendix 48 skipped for length)", "none")
slide("P01", "P", 37, "The path forward starts with real mess. A lot with no mass, a heavy mineral figure of one hundred forty percent, a certificate that expires before it was issued. All of it would load without complaint.",
      [["lot with no mass; 140 percent heavy mineral; certificate expires before issue", "deck slide 37 table"], ["every defect would load without complaint", "deck slide 37 footer"]])
slide("P02", "P", 40, "SHACL is how the graph says no. We'd start by validating before load and writing rules as SPARQL queries, which this demo already does. Native validation is an upgrade to confirm with Altair.",
      [["validate before load; rules as SPARQL; native validation to confirm with Altair", "deck slide 40 table and notes"], ["rules as SPARQL already proven in this demo", "deck slide 40 row B"]])
slide("P03", "P", 43, "Land and expand in three phases: one site and one use case first, then the Western Australian chain, then growth assets: the Eneabba refinery and Balranald. Scope and timing are indicative.",
      [["three phases: one site one use case; the WA chain; growth assets (Eneabba, Balranald)", "deck slide 43"], ["scope and timing indicative", "deck slide 43 footer"]])
slide("P05", "P", 46, "The next step is one site, one use case, real systems, validated by SHACL. The standards are open, the platform is proven, and the model is already built. The ask is a scoped proof of concept.",
      [["next step one site one use case real systems validated by SHACL", "deck slide 46"], ["standards open, platform proven, model built; ask is a scoped proof of concept", "deck slide 46 notes"]])
slide("P06", "P", 47, "Thank you for watching. The contact details are on the screen.",
      [["contact details on screen", "deck slide 47"]], dwell=2.0)


MEASURED = {}
_vl = os.path.join(ROOT, "tests", "e2e", "artifacts", "film", "voice", "voice_log.json")
if os.path.exists(_vl):
    for _r in json.load(open(_vl, encoding="ascii")):
        MEASURED[_r["id"]] = _r["duration_s"]


def est_audio(b):
    if b["id"] in MEASURED:
        return round(MEASURED[b["id"]], 2)
    return round(len(b["text"]) * CPS_S, 2)


def planned(b):
    v = est_audio(b)
    if b["kind"] == "slide":
        return round(LEAD + v + TAIL + b["dwell_s"], 2)
    if b["intent_or_landing"] == "intent":
        return round(max(v + LEAD + TAIL, b["act_s"] + 1.0), 2)
    return round(LEAD + v + TAIL + b["dwell_s"] + LOOK + max(0.0, b["act_s"] - v) * 0.5, 2)


def main():
    t = 0.0
    voice_total = 0.0
    out = {"title": "MiningOpsApp full narrated walkthrough (stage 1 beat sheet)", "voice": "Darth_MikGeorg (Kokoro, offline)",
           "fps": 23, "viewport": {"width": 1600, "height": 900, "dsf": 2}, "frame": {"width": 1920, "height": 1080},
           "caption_strip_css_px": 104, "as_of": "30 Sep 2026", "scenes": SCENES, "beats": []}
    ids = set()
    for b in BEATS:
        assert b["id"] not in ids, b["id"]
        ids.add(b["id"])
        v = est_audio(b)
        p = planned(b)
        row = dict(b)
        row["voice"] = "Darth_MikGeorg"
        row["est_audio_ms"] = int(v * 1000)
        row["planned_ms"] = int(p * 1000)
        row["start_ms"] = int(t * 1000)
        row["audio_ms"] = int(MEASURED[b["id"]] * 1000) if b["id"] in MEASURED else None
        row["chars"] = len(b["text"])
        out["beats"].append(row)
        t += p
        voice_total += v
    out["total_planned_s"] = round(t, 1)
    out["total_voice_est_s"] = round(voice_total, 1)
    out["density_est"] = round(voice_total / t, 3)
    out["beat_count"] = len(BEATS)
    p = os.path.join(ROOT, "tests", "e2e", "artifacts", "film", "beats.json")
    with open(p, "w", encoding="ascii") as f:
        json.dump(out, f, indent=1, ensure_ascii=True)
    print("beats", len(BEATS), "planned_s", out["total_planned_s"], "voice_s", out["total_voice_est_s"], "density", out["density_est"])
    # per scene stats
    stats = {}
    for r in out["beats"]:
        s = stats.setdefault(r["scene"], [0, 0.0, 0.0])
        s[0] += 1
        s[1] += r["planned_ms"] / 1000.0
        s[2] += r["est_audio_ms"] / 1000.0
    for k, v in stats.items():
        print("  %-3s beats %2d planned %6.1f s voice %6.1f s dens %.2f" % (k, v[0], v[1], v[2], v[2] / v[1]))
    longest = sorted(out["beats"], key=lambda r: -r["chars"])[:5]
    print("longest texts:", [(r["id"], r["chars"]) for r in longest])
    return out


def fmt_t(s):
    s = int(round(s))
    return "%d:%02d" % (s // 60, s % 60)


def write_docs(out):
    d = os.path.join(ROOT, "docs", "film")
    os.makedirs(d, exist_ok=True)
    L = []
    L.append("# Beat sheet - MiningOpsApp full narrated walkthrough (stage 1)\n")
    L.append("Generated by tests/e2e/film/gen_beats.py from the same data as tests/e2e/artifacts/film/beats.json. Do not edit by hand; edit the generator.\n")
    L.append("Decisions (author, final): new film, the old demo film is ignored; follow the deck Iluka_Presentation.pptx; each deck question is shown as the REAL slide image, then cut to the live app doing the same thing; voice Darth_MikGeorg, offline (Kokoro, recipe Video_Production.md 4.5 H.2); English; captions burned in; length flexible; 23 fps (rule 16).\n")
    L.append("## Production settings\n")
    L.append("| Item | Value |\n|---|---|")
    L.append("| App viewport | 1600 x 900 CSS px (16:9), deviceScaleFactor 2, captured with demo-polish.js startCapture, rendered/assembled at 23 fps to a 1920 x 1080 frame |")
    L.append("| Why 1600 x 900 | 1440 x 900 and 1920 x 1080 both rehearsed with identical results (26 of 27 steps PASS, no nav label or button clipped); 16:9 is needed to match the 16:9 slide images, and 1600 gives larger type than 1920 after scaling. The graph card needs at least about 1024 wide. |")
    L.append("| Caption strip | burned in by the page (as demo-film-record.js STRIP, 104 css px high, step number only, no total); slide beats use the same strip: the slide image is scaled to fit above it |")
    L.append("| Role / sessions | manager for everything except R04-R05 (viewer). Sign-in is off camera; capture starts on the signed-in page; every session ends with the XAS logout call (never /logout) |")
    L.append("| Voice | one WAV per beat, 24 kHz mono, Darth_MikGeorg; 12.4 characters per second measured on the first five clips (0.0805 s per character); voice text equals caption text; codes are respelled only inside tests/e2e/film/pronunciations.json |")
    L.append("| Timing model | slide beat = 0.4 s lead + voice + 1.2 s tail + dwell; app intent beat = max(voice + 1.6, action + 1.0); app landing beat = 0.4 + voice + 1.2 + dwell (+ half of any action time beyond the voice). Final lengths replace the estimates when the real clips are measured |")
    L.append("| Slide images | tests/e2e/artifacts/film/slides/slide-01.png to slide-48.png, 1920 x 1080, exported from the pptx through PowerPoint COM (tests/e2e/film/export_pptx_slides.py); the PDF in the deck folder has only 45 pages, so it was not used (its PNGs are kept in slides-pdf/) |")
    L.append("| Cursor | demo-polish click glide plus ripple; the cursor is parked on the nav bar between actions; dropdowns and radio choices mark the option (rule 10) |")
    L.append("| Dialogs | the only dialog is the Add task popup (R03): Cancel, never Save. No data is changed anywhere in the film |")
    L.append("| Graph-down (R06-R07) | needs the app started with GRAPH_BASE_URL=http://127.0.0.1:18080 and analysis/tools/stage6/tmp/n99/graph-proxy.js running; record the whole film that way (proxy up) and flip the proxy down only for R06-R07. Rehearsed on 2026-11-15; app restored to its normal constants afterwards |\n")
    L.append("## Totals\n")
    L.append("| Beats | Planned running time | Estimated narration | Estimated density |\n|---|---|---|---|")
    L.append("| %d | %s (%.0f s) | %.0f s | %.0f percent |\n" % (out["beat_count"], fmt_t(out["total_planned_s"]), out["total_planned_s"], out["total_voice_est_s"], out["density_est"] * 100))
    L.append("Density target 55 to 65 percent, fail above 70 (rule 13). Slide beats are voice-first, so the app beats carry the quiet time.\n")
    L.append("## Deck question to app finding map\n")
    L.append("| Deck question | Slides | App detector (Detector column) | Finding to open in the app | Severity | Case state at rehearsal |\n|---|---|---|---|---|---|")
    mp = [("Q1 Castellon claim", "26, 27", "S3", "SHP-ZR-024", "High", "Open"), ("Q2 Synthetic rutile below spec", "28", "S1", "Capel Kiln Line SR2 10 Jul 2026", "Medium", "Open"),
          ("Q3 Grade reconciliation", "29", "S2", "CAT-N-018", "Low", "Open"), ("Q4 Balranald steering", "30", "S5", "BAL-RUM-03", "Medium", "Open"),
          ("Q5 Third-party reagent (simulated)", "31", "S7", "TP_002 (Northern Monazite Resources Pty Ltd)", "Low", "Open"), ("Q6 Monazite radiation", "32", "S4", "MONAZITE_NAR_20260819", "Critical", "No case"),
          ("Q7 Certification", "33", "S6", "INC00027", "High", "Open"), ("Q8 Rehabilitation", "34", "S8", "OBL-007", "High", "Open")]
    for m in mp:
        L.append("| %s | %s | %s | %s | %s | %s |" % m)
    L.append("")
    L.append("## Scenes\n")
    L.append("| Scene | Title | Deck slides used | App pages |\n|---|---|---|---|")
    for s in out["scenes"]:
        L.append("| %s | %s | %s | %s |" % (s["id"], s["title"], s["deck_slides"], s["app"]))
    L.append("")
    L.append("## Beats\n")
    L.append("Columns: id, planned start (estimate), planned seconds, kind (slide, or app intent before the click / landing after the screen paints), source, caption and voice text (identical), action.\n")
    cur = None
    for r in out["beats"]:
        if r["scene"] != cur:
            cur = r["scene"]
            title = [s for s in out["scenes"] if s["id"] == cur][0]["title"]
            L.append("\n### Scene %s - %s\n" % (cur, title))
        src = ("slide %d" % r["source"]["slide"]) if r["kind"] == "slide" else r["source"]["page"]
        L.append("**%s** | start %s | %.1f s | %s | %s | role %s" % (r["id"], fmt_t(r["start_ms"] / 1000.0), r["planned_ms"] / 1000.0, r["intent_or_landing"], src, r["role"]))
        L.append("")
        L.append("> %s" % r["text"])
        L.append("")
        if r["kind"] == "slide":
            L.append("- Action: show %s (real slide image). No app action." % r["action"]["show"])
        else:
            for st in r["action"]["steps"]:
                bits = ["%s=%s" % (k, v) for k, v in st.items() if k != "do"]
                L.append("- %s %s" % (st["do"], "; ".join(bits)))
        L.append("")
    with open(os.path.join(d, "beat-sheet.md"), "w", encoding="ascii") as f:
        f.write("\n".join(L) + "\n")

    C = []
    C.append("# Claims table (rule 13) - MiningOpsApp full narrated walkthrough\n")
    C.append("One row per narrated line. Every number, name, role and status word the line asserts, with the source it was read from. Stage 1 sources: the live app rehearsal on 2026-11-15 (as-of 30 Sep 2026, screenshots in tests/e2e/artifacts/film/rehearsal/), the deck text reference/Iluka_Presentation_text.md (slide numbers), and the proven journeys. The column OK says where the check stands now; the frame-by-frame check (ffmpeg -ss t -frames:v 1) is repeated at stage 2 on the final take and the completion line is written then.\n")
    C.append("Numbers in the voice are spelled for the ear; this table keeps the digits.\n")
    C.append("| Beat | Planned t | Line | Asserts | Source (on screen / deck) | OK |\n|---|---|---|---|---|---|")
    n = 0
    for r in out["beats"]:
        asserts = "; ".join(c[0] for c in r["claims"])
        srcs = "; ".join(c[1] for c in r["claims"])
        ok = "deck-checked (stage 1)" if r["kind"] == "slide" else ("source read in rehearsal (frame check at take)" if "not visible on screen" not in srcs else "source is a test report, not a frame (stated in the line)")
        C.append("| %s | %s | %s | %s | %s | %s |" % (r["id"], fmt_t(r["start_ms"] / 1000.0), r["text"].replace("|", "/"), asserts.replace("|", "/"), srcs.replace("|", "/"), ok))
        n += 1
    C.append("")
    C.append("Lines listed: %d. Frame check status: PENDING for the final take (stage 2). Known value notes: the evidence row variance reads -20.55208333 on screen and the line says about minus twenty point six (rounds correctly; the deck shows -20.6); the BAL-RUM-03 deviation event shows its date as 5/4/2026 (US order, means 4 May); the film never reads that date aloud." % n)
    with open(os.path.join(d, "claims-table.md"), "w", encoding="ascii") as f:
        f.write("\n".join(C) + "\n")


if __name__ == "__main__":
    o = main()
    write_docs(o)
