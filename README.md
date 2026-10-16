# The most powerful dev tools. As a dummy, for dummies.

A one-page version of a Figma deck about using Claude Code (the desktop app) and the tools it connects to: Figma, GitHub, Vercel, Supabase and Railway. Written by a designer, for designers. You describe the outcome and Claude does the code, git and deploys.

22 slides stacked on one page, about 30 minutes if you present it.

## Reading it

Scroll, or use the nav on the left. The nav is drawn like a git graph: each tool is a line, each slide is a commit on it. Slide titles stick to the top and shrink as you scroll through a slide.

Things to try: pick something in the mock preview on the "Point at it" slide, tick off the setup steps, hover the four terms on the GitHub diagram, press "Play the loop" on the last feature slide.

## Presenting it

Press **P** (or the Present button). The nav hides, every slide fills the screen, and a timer and notes drawer appear.

| Key | What it does |
| --- | --- |
| `P` | Start or stop presenting |
| `→` `Space` `J` | Next slide |
| `←` `K` | Previous slide |
| `Home` `End` | First or last slide |
| `N` | Speaker notes (about 30 minutes of timings are built in) |
| `F` | Fullscreen |
| `?` | Show the keys |
| `Esc` | Close this, or stop presenting |

Add `?present` to the address to open straight into presenting. `#figma` style links jump to a slide.

## Files

```
index.html          all 22 slides and their speaker notes
assets/style.css    the look: flat dark grey, Geist, outlined pills, one white callout per idea
assets/app.js       nav, sticky heads, demos, presenter mode (no dependencies)
assets/img/         screenshots, as WebP
tools/              the script that first generated index.html, and the speaker notes it used
```

No build step. Edit `index.html` and push. `tools/gen.py` is only how the first version was made; running it again overwrites `index.html`, so leave it alone unless you want to start over. To change a slide, ask Claude Code: "change slide 12 so it says...".

## Hosting

GitHub Pages, from the root of the default branch. `.nojekyll` is there so files are served as they are.

## Credits

- The Figma editor and Vercel deployments screenshots are the author's own windows. The Vercel image has commit messages, avatars and the author handle blurred.
- The GitHub, Supabase and Railway images come from each company's public docs and site.
- The Claude Code video is Anthropic's, embedded from YouTube only when you press play.
- Not affiliated with or endorsed by Anthropic, Figma, GitHub, Vercel, Supabase, Railway or Wiley. "For Dummies" is a trademark of John Wiley & Sons.
- Type is Geist, from Google Fonts.
