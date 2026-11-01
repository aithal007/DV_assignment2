# Figure 4: paired changes PCP

This selected view compares changes from 2015 to 2020 for the same 175 countries. Each of the four differences is computed after joining by country code. The default brush selects 39 countries gaining 20?30 percentage points in internet use. Georgia, Brunei and Uzbekistan are named examples, selected to illustrate different combinations rather than estimate population frequencies.

Open index.html locally or through the supplied launcher. Data are embedded in data.js, so no fetch request or external library is needed. The shared countryCurve function is supplied at ../../web/pcp-curves.js. Drag on the internet-use axis, edit the range, reorder axes, hover over records, or compare straight and bundled paths. Zero is aligned and axes use separate fixed symmetric ranges: ?50, ?25, ?25 and ?100. No observation is clipped. Bundling is 20% toward the selected or unselected group's average path and retains exact axis intersections.

Rebuild the PNG, SVG, CSV and embedded records with python -X utf8 scripts/build_change_pcp.py from the submitted folder. Check browser interactions with node scripts/audit_change_pcp.mjs when the documented Playwright/Edge runtime is available. Independent difference checks are in scripts/verify_approved_replacements.py.

The PNG is the report illustration. paired_changes.csv retains all countries and selection membership. validation.json records the selected count and named values; browser_validation.json records actual pointer brushing, reordering, hover, straight/bundled switching and reset. The full GUI capture is also in images/gui/pcp_changes_2015_2020.png.

Method references: September 22 and 24 course lectures; https://syntagmatic.github.io/parallel-coordinates/ ; https://arxiv.org/abs/1109.6073 . The plot uses gently constrained individual curves, rather than the filled density ribbons in the September 22 lecture.
