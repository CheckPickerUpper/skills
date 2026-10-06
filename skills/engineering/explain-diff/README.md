# explain-diff

Explains a code change, diff, branch, commit or PR as one self-contained page:
background, intuition with a worked example, a walkthrough in execution order,
what could break, and a quiz.

## Where it comes from

This skill is based on Geoffrey Litt's
[`explain-diff` gist](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524).
His prompt set the shape this skill keeps: explain a change the way a good
teacher would (background, intuition, code, quiz), with diagrams instead of
ASCII art and a page that works on a phone. The gist has an HTML version, a
Notion version, and a revised HTML version that adds quiz-quality rules.

## What changed and why

| Change | Why |
|---|---|
| **The quiz is written as JSON and a script places the answers.** `scripts/build.py` shuffles options with a seed and balances the correct answer's position across A–D. | The gist's most common complaint: the right answer was usually in a predictable spot. Telling a model to "randomize" doesn't work, because models don't shuffle well. A script does. |
| **The build refuses quizzes you can pass by length.** If the correct option is clearly the longest too often, the page is not written. | The other common complaint was that picking the longest answer usually won. The gist only asked the model to keep lengths similar; nothing checked. |
| **`--quiz chat` asks free-response questions in the conversation and grades them.** | Commenters found that free response tests understanding far better than multiple choice, which can't fully avoid guessable options. |
| **The diff, commit messages and PR text are treated as data, never instructions.** | A commenter pointed out the prompt-injection risk when explaining someone else's PR. The gist didn't cover it. |
| **A fixed template holds all CSS and JS; the model writes only the body.** | The gist had the model write a full HTML page, CSS and JS included, on every run. The template removes those tokens and gives consistent diagrams, callouts, light/dark mode and a mobile layout. |
| **The build checks the body**: no `<script>`, no inline handlers, no remote assets, and at least one section. | The gist asked for "no CDN dependencies" and safe escaping but didn't enforce them. |
| **The walkthrough follows execution order**, with each step linked to `path:line`. | "Group by understandable categories" was vague. Flow order was one of the improvements commenters shared. |
| **New "What could break" section.** | For a reviewer this is often the most useful part, and the gist had nothing for it. |
| **Length scales with the change**: a small fix gets little background and 2 questions. | Nothing stopped a 3-line fix from getting a 2,000-word explainer. |
| **One skill, with HTML or Markdown output.** The Notion version was dropped. | The two gist files repeated the same content rules and would drift apart. Markdown is the cheapest format; Notion added tool-call overhead without saving tokens. |
| **Validation**: the build refuses bad input, and the skill screenshots the page at 375px and 1200px when a browser is available. | "Validate before delivery" in the gist had no concrete checks. The phone-width check has already caught one layout bug in the template. |
