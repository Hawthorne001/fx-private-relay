# Relay: "Base load" Engineer playbook

Starting in H2'24, Relay ENGR team expanded the "Release Engineer" role into a "Base
load Engineer" role who handles consistent expected work like releases and dependency
updates, and who fields un-planned incoming work requests like bug reports and customer
support requests. (The term "[base load][]" comes from electrical grids, where it
describes the minimum level of demand over a span of time.)

[base load]: https://en.wikipedia.org/wiki/Base_load

## Rotation

Relay ENGRs rotate thru the "Base load" role every 2 weeks on Tuesdays, to coincide with
our weekly Tuesday release schedule. The current Relay ENGR team consists of these
engineers who rotate thru the role:

1. [@groovecoder](https://github.com/groovecoder)
1. [@joeherm](https://github.com/joeherm)
1. [@vpremamozilla](https://github.com/vpremamozilla)
1. [@jwhitlock](https://github.com/jwhitlock)

## Daily routine

Your primary role is to perform the checks and make sure the necessary work gets done.
You don't have to perform every task yourself. When you check any of the channels below,
you may delegate the resulting task to the most appropriate party.

The work is tracked in the [Relay Base Load Engineer Log][], along with current long-term
issues that are being monitored or worked on. If that document and this one disagree, usually
the log is up-to-date.

If any items found during the checks below are [incident-level severity][], you are
likely to take the role of engineering lead for the incident unless you delegate to
another more appropriate party.

1. Check [Security Dependabot Alerts][security-dependabot-alerts] for any critical
   security updates to make
1. Check #relay-alerts for any critical operational issues to fix
1. Check the [Sentry Releases][sentry-releases] report to watch for any new issues
1. Check #relay-jira-triage for any new tickets.
   - is assigned to a Sprint
   - and includes a [work category][work-categories]
1. Check [Bugzilla][bugzilla-passmgr-relay-1w] for recent [Password Manager bugs][bugzilla-passmgr] mentioning [Relay][bugzilla-passmgr-relay]
1. Check #privsec-customer-experience channel for any urgent inbound CX requests
1. Check [dependabot pull requests][dependabot-prs]
   (see the [Dependency Updates doc][dependency-updates-doc])
1. Co-ordinate, re-tag for [stage fixes][stage-fixes] as needed

[incident-level severity]: https://mozilla-hub.atlassian.net/wiki/spaces/MIR/pages/20512894/Incident+Severity+Levels

## Mondays

1. Daily routine
2. Prepare release for tomorrow
   - Look thru [What's Deployed][whats-deployed] tool to make sure all the
     commits on stage are ready to go to prod.
   - You can also run a [comparison on GitHub][github-compare] between [the stage
     version][stage-version] and [the prod version][prod-version].
   - [Write SRE ticket, mention authors, reference in release notes][release-to-prod]

## Tuesdays

1. Daily routine
2. SRE processes ticket to release the tag to production
3. Update [Github Release][github-releases] to current release
4. Monitor [Sentry Releases][sentry-releases] for new production issues
5. [Run e2e tests][run-e2e-tests] against the prod environment via GitHub Actions.
6. (On your 3rd Tuesday) Hand-off base load duties to next engineer in rotation

## Wednesdays

1. Daily routine
2. Before releasing to Stage, [run e2e tests][run-e2e-tests] against the dev environment via GitHub Actions.
   - Ensure that the e2e tests are passing.
   - If e2e Playwright tests are flaky--fails to pass for reasons outside of legitimate Relay bug--consider making the tests more reliable by using the [locators][playwright-locators], [auto-retrying assertions][playwright-auto-retrying-assertions], or [fixtures][playwright-fixtures]. For more suggestions on making Playwright tests more reliable or efficient, see [documentation on FxA test improvements][fxa-test-improvements].
3. [Release to stage][Release-to-stage] (tag, Github release notes)
   - Ping all the engineers who have changes in the release to:
     - Move cards to “Ready to Test” if necessary
     - Include instructions for QA to test
   - Confirm any hotfixes are also in the new tag

## Thursday and Fridays

1. Daily routine

## Sick Days/ Personal Emergencies

Contact other engineers to transfer Base Load Engineer responsibilities to another engineer in case of illness or personal emergency.

[security-dependabot-alerts]: https://github.com/mozilla/fx-private-relay/security/dependabot
[whats-deployed]: https://whatsdeployed.io/s/60j/mozilla/fx-private-relay
[github-compare]: https://github.com/mozilla/fx-private-relay/compare/
[stage-version]: https://stage.fxprivaterelay.nonprod.cloudops.mozgcp.net/__version__
[prod-version]: https://relay.firefox.com/__version__
[github-releases]: https://github.com/mozilla/fx-private-relay/releases
[run-e2e-tests]: https://github.com/mozilla/fx-private-relay/actions/workflows/playwright.yml
[playwright-locators]: https://playwright.dev/docs/locators
[playwright-auto-retrying-assertions]: https://playwright.dev/docs/test-assertions#auto-retrying-assertions
[playwright-fixtures]: https://playwright.dev/docs/test-fixtures
[fxa-test-improvements]: https://docs.google.com/presentation/d/1dSASq9xcaA8DuQM_1_Ab6q5_ScBpvqI9NPHvovkA-wU/edit#slide=id.g276e3207c4d_1_427
[release-to-stage]: https://github.com/mozilla/fx-private-relay/blob/main/docs/release_process.md#release-to-stage
[sentry-releases]: https://mozilla.sentry.io/releases/
[stage-fixes]: https://github.com/mozilla/fx-private-relay/blob/main/docs/release_process.md#stage-fixes
[release-to-prod]: https://github.com/mozilla/fx-private-relay/blob/main/docs/release_process.md#release-to-prod
[dependabot-prs]: https://github.com/mozilla/fx-private-relay/pulls/app%2Fdependabot
[dependency-updates-doc]: https://github.com/mozilla/fx-private-relay/blob/main/docs/dependency-updates.md
[bugzilla-passmgr-relay-1w]: https://bugzilla.mozilla.org/buglist.cgi?list_id=17370610&classification=Client%20Software&classification=Developer%20Infrastructure&classification=Components&classification=Server%20Software&classification=Other&short_desc=relay&component=Password%20Manager&resolution=---&query_format=advanced&short_desc_type=allwordssubstr&product=Toolkit&chfieldfrom=-1w&chfield=%5BBug%20creation%5D
[bugzilla-passmgr-relay]: https://bugzilla.mozilla.org/buglist.cgi?component=Password%20Manager&list_id=17381002&short_desc_type=allwordssubstr&query_format=advanced&resolution=---&short_desc=Relay&product=Toolkit
[bugzilla-passmgr]: https://bugzilla.mozilla.org/buglist.cgi?product=Toolkit&component=Password%20Manager&resolution=---&list_id=17380991
[work-categories]: https://docs.google.com/document/d/1fgcParg78LZkhsZSwFWkPBWeibNF7TYAHLQ9a2VKHU0/edit?tab=t.0#heading=h.ymszsodqgebv
[Relay Base Load Engineer Log]: https://docs.google.com/document/d/1eftTFds1Z2smDqPvcYSwFacQ26nynsMbvW1TUB--4FA/edit?usp=sharing
