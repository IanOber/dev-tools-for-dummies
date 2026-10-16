#!/usr/bin/env python3
"""Slide content -> index.html.

This is how the first version of index.html was made. Since then index.html is the
source of truth, so running this again overwrites any edits made to it by hand.
Speaker notes come from notes.json next to this file.

    python3 tools/gen.py <folder to write index.html into>
"""
import html, json, re, sys, pathlib

SCRATCH = pathlib.Path(__file__).parent
SITE = pathlib.Path(sys.argv[1])
E = lambda s: html.escape(s, quote=True)

notes = {o["n"]: o for o in json.load(open(SCRATCH / "notes.json"))}

def note_html(n):
    paras = [p.strip() for p in notes[n]["text"].split(" ⏎ ")]
    return "".join(f"<p>{E(p)}</p>" for p in paras)

# ---------------------------------------------------------------- slide shell
TOTAL = 22

def shell(slide_id, n, title, sub, chapter, body, extra_cls=""):
    sub_html = f'\n        <p class="slide__sub">{E(sub)}</p>' if sub else ""
    return f'''
<section class="slide{extra_cls}" id="{slide_id}" data-n="{n}" data-title="{E(title)}" data-chapter="{E(chapter)}" data-time="{notes[n]["t"]}">
  <div class="slide__head">
    <div class="slide__headin">
      <h2 class="slide__title">{E(title)}</h2>{sub_html}
    </div>
    <p class="slide__count" aria-hidden="true"><span class="slide__chapter">{E(chapter)}</span><span><b>{n}</b> / {TOTAL}</span></p>
  </div>
  <div class="slide__body">
{body}
  </div>
  <aside class="slide__notes" hidden>{note_html(n)}</aside>
</section>'''

LOOP_SVG = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13.5 8a5.5 5.5 0 1 1-1.9-4.15"/><path d="M13.6 2.2v3h-3"/></svg>'

def pills(items, cls=""):
    return f'<ul class="pills {cls}">' + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>"

# ---------------------------------------------------------------- intro slide (Claude Code, Figma, GitHub, Vercel, Supabase, Railway)
def intro(slide_id, n, title, sub, chapter, bullets, prompt, media, caps):
    pts = "".join(f"<li>{E(b)}</li>" for b in bullets)
    body = f'''    <div class="cols">
      <div class="stack">
        <ul class="points">{pts}</ul>
        <div class="prompt">
          <p class="prompt__label">Example prompt</p>
          <p class="prompt__text">{E(prompt)}</p>
          <button class="copy" type="button" data-copy="{E(prompt)}">Copy prompt</button>
        </div>
      </div>
{media}
    </div>
    <div class="caps">
      <p class="caps__label">What it can do</p>
      {pills(caps)}
    </div>'''
    return shell(slide_id, n, title, sub, chapter, body)

def shot(src, alt, w, h, caption, link_label, link_url):
    return f'''      <figure class="shot">
        <div class="shot__img"><img src="assets/img/{src}" alt="{E(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async"></div>
        <figcaption>{E(caption)}</figcaption>
        <a class="shot__link" href="{link_url}" target="_blank" rel="noopener">{E(link_label)}</a>
      </figure>'''

# ---------------------------------------------------------------- setup slide
def setup(slide_id, n, title, sub, chapter, use, day, access, steps):
    lis = []
    for i, s in enumerate(steps, 1):
        last = i == len(steps)
        num = LOOP_SVG if last else str(i)
        cls = "step step--loop" if last else "step"
        lis.append(f'''          <li><label class="{cls}"><input type="checkbox"><span class="step__row"><span class="step__num">{num}</span><span class="step__text">{E(s)}</span></span></label></li>''')
    body = f'''    <div class="cols">
      <div class="sections">
        <div class="info"><p class="info__label">Use it when</p><p>{E(use)}</p></div>
        <div class="info"><p class="info__label">Day to day</p><p>{E(day)}</p></div>
        <div class="info"><p class="info__label">Access it uses</p><p>{E(access)}</p></div>
      </div>
      <div class="steps" data-steps>
        <p class="steps__label">How to set it up</p>
        <ol>
{chr(10).join(lis)}
        </ol>
        <p class="steps__tally" aria-live="polite" data-tally></p>
      </div>
    </div>'''
    return shell(slide_id, n, title, sub, chapter, body)

slides = []

# ============================================================== 02 Claude Code (video facade)
video = '''      <figure class="shot">
        <button class="video" type="button" data-yt="rWaQSQEm_aY" data-title="The new Claude Code desktop app, redesigned for parallel agents" aria-label="Play video: The new Claude Code desktop app, redesigned for parallel agents">
          <span class="video__face">
            <span class="video__play"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6 4.5v15l13-7.5z"/></svg></span>
            <span class="video__title">The new Claude Code desktop app</span>
            <span class="video__meta">Official video from Anthropic. Loads from YouTube when you press play.</span>
          </span>
        </button>
        <figcaption>Sessions on the left, the conversation in the middle, a live preview on the right. Diff, terminal and plan panes open alongside.</figcaption>
        <a class="shot__link" href="https://code.claude.com/docs/en/desktop" target="_blank" rel="noopener">code.claude.com/docs</a>
      </figure>'''
slides.append(intro("claude-code", "02", "Claude Code", "Build", "Claude Code",
    ["You describe the outcome. It handles the code, git and GitHub.",
     "Reads your Figma frames through connectors and builds them in your project folder.",
     "Shows a plan, a diff and a live preview, so you review before anything ships."],
    "read this figma frame, plan the build, implement it in this project, and show it in the preview",
    video,
    ["Reads designs", "Plans first", "Builds", "Live preview", "Reviews diffs", "Opens PRs", "Parallel sessions"]))

# ============================================================== 03 its own thing
body = '''    <table class="grid grid--tabs">
      <thead><tr><th scope="col">Tab</th><th scope="col">What it&rsquo;s for</th><th scope="col">What it knows</th></tr></thead>
      <tbody>
        <tr><td data-label="Tab">Chat</td><td data-label="What it&rsquo;s for">Everyday conversations with Claude.</td><td class="muted" data-label="What it knows">Its own chat history.</td></tr>
        <tr><td data-label="Tab">Cowork</td><td data-label="What it&rsquo;s for">Dispatch and longer agentic work.</td><td class="muted" data-label="What it knows">Its own tasks and history. Dispatch can start a Code session with a task.</td></tr>
        <tr class="is-code"><td data-label="Tab">Code</td><td data-label="What it&rsquo;s for">Building software in a project folder.</td><td class="muted" data-label="What it knows">One session&rsquo;s history, the project folder, CLAUDE.md and auto memory. Nothing from your Chat or Cowork conversations.</td></tr>
      </tbody>
    </table>
    <div class="cols cols--tight">
      <div class="callout"><p class="callout__text">Each tab keeps its own conversations. What I tell Chat or Cowork doesn&rsquo;t carry into Code.</p></div>
      <p class="note">Connectors and skills are shared: set them up once under Customize.</p>
    </div>'''
slides.append(shell("own-thing", "03", "Claude Code is its own thing.", "Separate from Chat and Cowork.", "Claude Code", body))

# ============================================================== 04 folders
body = '''    <div class="cols">
      <div>
        <h3 class="colhead">Your folder</h3>
        <div class="sections sections--compact">
          <div class="info"><p class="info__label">Project folder</p><p>Pick a folder or repo when you start a session. Claude reads, edits and runs commands there.</p></div>
          <div class="info"><p class="info__label">Worktrees</p><p>For Git projects, each session can work in its own copy under .claude/worktrees, so parallel tasks don&rsquo;t collide.</p></div>
          <div class="info"><p class="info__label">Terminal</p><p>The built-in terminal opens in the same folder, with the same environment as Claude.</p></div>
        </div>
      </div>
      <div>
        <h3 class="colhead">What it remembers</h3>
        <div class="sections sections--compact">
          <div class="info"><p class="info__label">Session history</p><p>Each session has its own history, saved on your computer. A new session starts fresh.</p></div>
          <div class="info"><p class="info__label">CLAUDE.md</p><p>A file in the project with instructions you write. Claude reads it at the start of every session.</p></div>
          <div class="info"><p class="info__label">Auto memory</p><p>Notes Claude writes itself from your corrections and preferences, carried into later sessions.</p></div>
        </div>
      </div>
    </div>
    <div class="tree">
      <p class="tree__label">What that looks like on disk</p>
<pre><code>my-project/            <em>the folder I pick</em>
&#9500;&#9472; CLAUDE.md           <em>instructions I write</em>
&#9500;&#9472; .claude/
&#9474;  &#9500;&#9472; worktrees/       <em>one copy per parallel session</em>
&#9474;  &#9492;&#9472; settings, skills, rules
&#9492;&#9472; &hellip;your files
~/.claude/             <em>global settings, skills, rules</em></code></pre>
    </div>'''
slides.append(shell("folders", "04", "Folders on your computer.", "Plus its own saved context.", "Claude Code", body))

# ============================================================== 05 Claude Code setup
slides.append(setup("claude-code-setup", "05", "Claude Code: setup and use.", "Install it. Open a folder. Go.", "Claude Code",
    "Any build or edit task: reading a design, changing code, running the app.",
    "Describe outcomes, not commands. Claude handles the files, git and tooling. Add services any time from + → Connectors.",
    "Your project folder, plus whatever the permission mode and connectors allow.",
    ["Install the Claude desktop app and sign in. Claude Code needs a paid plan.",
     "Open the Code tab and choose your project folder.",
     "For Git projects, pick the worktree option. Claude manages the branch.",
     "Pick a permission mode, then describe what you want.",
     "Review the preview and the diff, and say what to change. No terminal needed.",
     "Rinse and repeat: next task, next session."]))

# ============================================================== 06 point at it
tools = '''<div class="tools" role="toolbar" aria-label="Markup tools (demo)">
            <button type="button" class="tool is-on" data-tool="select" aria-pressed="true" aria-label="Select"><svg viewBox="0 0 20 20" fill="currentColor"><path d="M4 2.5l11 6.2-4.7 1.3 2.6 4.8-1.9 1-2.6-4.8L4.8 14z"/></svg></button>
            <button type="button" class="tool" data-tool="box" aria-pressed="false" aria-label="Draw a box"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3.5" y="4.5" width="13" height="11" rx="1.5"/></svg></button>
            <button type="button" class="tool" data-tool="circle" aria-pressed="false" aria-label="Draw a circle"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="10" cy="10" r="6.5"/></svg></button>
            <span class="sep"></span>
            <button type="button" class="tools__btn" data-add disabled>Add to chat</button>
          </div>'''
body = f'''    <div class="cols">
      <div class="stack">
        <div class="ways">
          <div class="way"><h3>Select an element</h3><p>Pick it in the live preview (Cmd+Shift+S), then say what to change about it.</p></div>
          <div class="way"><h3>Mark it up</h3><p>Draw arrows, boxes, circles or text on the preview, then click Add to chat.</p></div>
          <div class="way"><h3>Comment on the diff</h3><p>Click any line to leave a comment. Submit all your comments at once.</p></div>
          <div class="way"><h3>Attach a reference</h3><p>Drop in a screenshot or mockup and say what to match.</p></div>
        </div>
      </div>
      <div class="demo" data-demo>
        <p class="demo__label">Try it. Pick something, then say what to change.</p>
        <div class="mock">
          <div class="mock__bar"><i></i><i></i><i></i><span>localhost:3000</span></div>
          <div class="mock__page" data-page>
            <h3 class="m-el m-head" data-label="Heading" tabindex="0" role="button" aria-pressed="false">Spring sale starts Friday</h3>
            <p class="m-el m-copy" data-label="Paragraph" tabindex="0" role="button" aria-pressed="false">Pick anything on this page, then tell Claude what to change.</p>
            <button class="m-el m-btn" data-label="Button" type="button" aria-pressed="false">Shop the sale</button>
            <div class="marks" data-marks aria-hidden="true"></div>
          </div>
          <div class="mock__tools">
          {tools}
          </div>
        </div>
        <div class="mock__asks">
          <span class="label">After pointing, I say:</span>
          <button type="button" class="pill-btn" data-ask="bigger">make this bigger</button>
          <button type="button" class="pill-btn" data-ask="tight">tighten the spacing here</button>
          <button type="button" class="pill-btn" data-ask="match">match the frame</button>
          <button type="button" class="pill-btn pill-btn--ghost" data-reset>Reset</button>
        </div>
        <div class="chat" data-chat aria-live="polite"><p class="hint">Click the heading, the paragraph or the button.</p></div>
      </div>
    </div>'''
slides.append(shell("point", "06", "Point at it. Say what to change.", "Selections become edit requests.", "Claude Code", body))

# ============================================================== 07 permissions
body = '''    <table class="grid grid--mode" data-modes>
      <thead><tr><th scope="col">Mode</th><th scope="col">What it does</th></tr></thead>
      <tbody>
        <tr tabindex="0" data-mode="manual"><td data-label="Mode">Manual</td><td class="muted" data-label="What it does">Asks before each edit and command.</td></tr>
        <tr tabindex="0" data-mode="accept"><td data-label="Mode">Accept edits</td><td class="muted" data-label="What it does">Auto-accepts file edits and common file commands like mkdir and mv. Still asks before other terminal commands.</td></tr>
        <tr tabindex="0" data-mode="plan"><td data-label="Mode">Plan</td><td class="muted" data-label="What it does">Reads and plans. No edits until you approve the plan.</td></tr>
        <tr tabindex="0" data-mode="bypass"><td data-label="Mode">Bypass permissions</td><td class="muted" data-label="What it does">Runs without permission prompts. Anthropic&rsquo;s docs recommend isolated environments. Safety checks still prompt on external sites.</td></tr>
      </tbody>
    </table>
    <div class="cols cols--tight">
      <button class="callout callout--btn" type="button" data-runit aria-describedby="runit-hint">
        <span class="callout__label">How I run it</span>
        <span class="callout__text">Accept edits or Bypass permissions on stable projects.</span>
      </button>
      <div class="stack stack--tight">
        <p class="note">Connections act with your account&rsquo;s access. Each service page lists what that covers.</p>
        <p class="note" id="runit-hint">Press the white box to mark the two modes on the table.</p>
      </div>
    </div>'''
slides.append(shell("permissions", "07", "Permissions.", "How much Claude asks first.", "Claude Code", body))

# ============================================================== 08 how it connects
body = '''    <div class="hub">
      <div class="hub__root"><b>Claude Code</b><span>Connectors reach into each tool.</span></div>
      <div class="hub__nodes">
        <a class="node" href="#figma"><b>Figma</b><small>Design</small></a>
        <a class="node" href="#github"><b>GitHub</b><small>Versioning</small></a>
        <a class="node" href="#vercel"><b>Vercel</b><small>Deployment</small></a>
        <a class="node" href="#supabase"><b>Supabase</b><small>Data</small></a>
        <a class="node" href="#railway"><b>Railway</b><small>Scheduled tasks</small></a>
      </div>
      <p class="hub__note">Added when a prototype needs real data or scheduled work.</p>
      <div class="also">
        <p class="also__label">Other Connectors</p>
        <ul class="also__row">
          <li><b>Cloudflare</b><span>Hosting and storage</span></li>
          <li><b>Notion</b><span>Docs and specs</span></li>
        </ul>
      </div>
    </div>'''
slides.append(shell("connects", "08", "How it all connects.", "Claude Code sits in the middle.", "How it connects", body))

# ============================================================== 09/10 Figma
slides.append(intro("figma", "09", "Figma", "Design", "Figma",
    ["The source of truth for styles, variables, grids and components.",
     "Manual control where precision matters. The agent takes repetitive canvas work.",
     "Claude reads your frames and variable bindings, so builds inherit your tokens."],
    "build this frame as a working page using my variables, text styles and components",
    shot("figma-editor.webp", "The Figma editor with a frame selected and its Fill bound to a variable in the right-hand panel.", 1500, 801,
         "That fill is bound to a variable (bg/charcoal). Claude reads bindings like that when it builds from your file.", "figma.com", "https://www.figma.com"),
    ["Design", "Components", "Variables and styles", "Prototyping", "Collaboration", "AI agent"]))
slides.append(setup("figma-setup", "10", "Figma: setup and use.", "Connect once. Work from links.", "Figma",
    "You have a frame or design system to build from.",
    "Paste a frame link, ask for the build, compare it with the design, and go again in small steps. Claude reads your styles and variables too.",
    "Your Figma access: reads frames, styles and variables, and can edit files you can edit.",
    ["In a session, click + → Connectors.",
     "Add Figma and sign in with your Figma account.",
     "Prep the file: components, auto layout, named layers, variables.",
     "Copy the link to the frame you want built.",
     "Paste it into the session and say what to build. Claude does the rest.",
     "Rinse and repeat: tweak the design, copy the new frame link, rebuild, compare."]))

# ============================================================== 11-14 GitHub
slides.append(intro("github", "11", "GitHub", "Version control", "GitHub",
    ["Every change is versioned, so any earlier state is recoverable. Claude makes the commits.",
     "Branches isolate experiments. Claude creates them and merges the keepers.",
     "Pull requests make a change reviewable. Claude opens them and watches the checks."],
    "take care of GitHub for me, and try a bolder layout so I can compare the two",
    shot("github-pr-comment.webp", "A GitHub pull request with a comment pinned to a point on an image.", 1500, 678,
         "Pull requests support comments on images, so visual changes get reviewed in place.", "github.com", "https://github.com"),
    ["Version history", "Branches", "Pull requests", "Collaboration", "Hosting (Pages)", "Automation (Actions)", "Issues"]))

rows = [
    ("take care of GitHub for me", "Creates the repo and keeps every change saved."),
    ("make the hover effect less intense", "Edits the code and saves it as a new version."),
    ("try a bolder version so I can compare", "Makes a branch and builds it. The original stays untouched."),
    ("I like that one", "Merges that branch into the main version."),
    ("go back to how it was", "Reverts to the earlier version."),
    ("do whatever works", "Picks the approach, does it, and tells you what it did."),
]
trs = "\n".join(f'        <tr><td data-label="I ask">&ldquo;{E(a)}&rdquo;</td><td class="muted" data-label="Claude does">{E(b)}</td></tr>' for a, b in rows)
body = f'''    <table class="grid grid--ask">
      <thead><tr><th scope="col">I ask</th><th scope="col">Claude does</th></tr></thead>
      <tbody>
{trs}
      </tbody>
    </table>
    <div class="callout callout--wide"><p class="callout__text">Git, GitHub, PRs and merges are Claude&rsquo;s job. Mine is the design call.</p></div>'''
slides.append(shell("github-ask", "12", "GitHub: I ask. Claude does.", "I’m a designer, not a developer.", "GitHub", body))

diagram = '''    <div class="diagram" data-diagram>
      <svg viewBox="0 0 1200 270" role="img" aria-label="Diagram: a branch leaves main, lives in its own worktree folder, goes through a pull request, and is merged back into main.">
        <path class="d-line draw" style="--len:1120" d="M40 70 H1160"/>
        <circle class="d-dot pop" style="--d:.3s" cx="40" cy="70" r="7"/>
        <circle class="d-dot pop" style="--d:.5s" cx="300" cy="70" r="7"/>
        <circle class="d-dot pop" style="--d:1.9s" cx="1160" cy="70" r="7"/>
        <text class="d-text" x="40" y="42">main</text>
        <g data-term="branch">
          <path class="d-line draw" style="--len:620" d="M300 70 C345 70 340 170 395 170 H645 C705 170 710 70 760 70"/>
          <circle class="d-dot pop" style="--d:.8s" cx="450" cy="170" r="7"/>
          <circle class="d-dot pop" style="--d:1s" cx="570" cy="170" r="7"/>
          <text class="d-text" x="400" y="150">branch</text>
        </g>
        <g data-term="worktree">
          <rect class="d-bracket" x="380" y="118" width="290" height="104" rx="18"/>
          <text class="d-text" x="380" y="248">worktree: this branch in its own folder</text>
        </g>
        <g data-term="pr">
          <path class="d-bracket" d="M668 160 C705 150 735 128 790 120"/>
          <text class="d-text" x="798" y="125">pull request</text>
        </g>
        <g data-term="merge">
          <circle class="d-dot pop" style="--d:1.5s" cx="760" cy="70" r="11"/>
          <text class="d-text" x="760" y="42" text-anchor="middle">merge</text>
        </g>
      </svg>
    </div>'''
terms = [
    ("branch", "Branch", "A parallel line of work in the same repository.", "Enables: trying a layout variant without touching the version that is live."),
    ("worktree", "Worktree", "A separate checkout of the repo, on its own branch, in its own folder.", "Enables: parallel Claude sessions that can’t overwrite each other’s files."),
    ("pr", "Pull request", "A proposal to merge one branch into another, shown as a diff.", "Enables: review, comments and automated checks before anything lands."),
    ("merge", "Merge", "Folding one branch’s changes back into another, usually main.", "Enables: approved work becoming the shared version, ready for Vercel to deploy."),
]
tl = "\n".join(f'''      <div class="term" data-for="{k}" tabindex="0">
        <h3>{E(h)}</h3>
        <p>{E(a)}</p>
        <p>{E(b)}</p>
      </div>''' for k, h, a, b in terms)
body = f'''{diagram}
    <div class="terms">
{tl}
    </div>
    <p class="reassure">Claude runs all of this. You just describe the change.</p>'''
slides.append(shell("github-terms", "13", "How GitHub works.", "Four terms. Claude handles all of them.", "GitHub", body))

slides.append(setup("github-setup", "14", "GitHub: setup and use.", "Connect once. No manual syncing.", "GitHub",
    "Any project you want versioned, shared or reviewed. Start from the first session.",
    "Claude makes the commits, branches and PRs, watches the checks, and can merge when they pass if the repo allows it. You review the preview and say what to change.",
    "Your repo access via the connector and gh: reads and writes code, branches and PRs.",
    ["Start the project in Claude Code, in a local folder.",
     "Connect GitHub once: + → Connectors → GitHub. Sign in to gh if it asks.",
     "Say: take care of GitHub for me. Claude creates the repo and the first commit.",
     "From then on, just describe the change. Claude handles branches, PRs and merges.",
     "Claude makes the commits, opens the PRs and merges them. You review the preview.",
     "Rinse and repeat: ask for the next change."]))

# ============================================================== 15-16 Vercel
slides.append(intro("vercel", "15", "Vercel", "Deploy", "Vercel",
    ["Builds and hosts every branch at its own URL.",
     "Reviewers test the real build on real devices, with no setup.",
     "Claude deploys it and sends you the link."],
    "deploy this branch to vercel and give me the preview url",
    shot("vercel-deployments.webp", "Vercel's Deployments page listing preview builds for branches and production builds from main.", 1272, 705,
         "Each row is a deployment. Preview rows are branch builds, and Production rows come from main.", "vercel.com", "https://vercel.com"),
    ["Deploy", "Preview URLs", "Hosting", "Domains", "Environment variables", "Rollbacks"]))
slides.append(setup("vercel-setup", "16", "Vercel: setup and use.", "Import the repo. Get previews.", "Vercel",
    "You want a shareable URL for review, or a host for the front end.",
    "Open the preview URL on a phone, send it for comments, and Claude ships it when it looks right. If a deploy fails, ask Claude to check the build output.",
    "Your Vercel team access: deploys, and edits project settings and variables.",
    ["Ask: put this on Vercel and send me a preview link.",
     "Sign in to Vercel if it asks. Claude picks the route: the CLI, or importing the GitHub repo.",
     "Claude adds the environment variables and fixes build errors.",
     "After that, each branch gets its own preview URL.",
     "Open the link on your phone and say what to change.",
     "Rinse and repeat: change, preview, ship."]))

# ============================================================== 17-18 Supabase
slides.append(intro("supabase", "17", "Supabase", "Data and auth", "Supabase",
    ["A hosted Postgres database, browsable and editable as a table.",
     "Sign-in and user management that Claude sets up for you.",
     "Real data to design against, including empty, loading and error states."],
    "add sign-in and a favorites table to this prototype using supabase",
    shot("supabase-table-editor.webp", "The Supabase table editor showing a table with rows of data.", 1500, 721,
         "The table editor shows live rows and lets you edit cells directly.", "supabase.com", "https://supabase.com"),
    ["Database", "Sign-in", "File storage", "Auto-generated APIs", "Realtime", "Edge functions"]))
slides.append(setup("supabase-setup", "18", "Supabase: setup and use.", "Connect it. Keep keys in .env.", "Supabase",
    "The prototype needs real data, sign-in or file storage.",
    "Describe the data, let Claude write the migration, then open the table editor to see the rows. Use real data to design empty, loading and error states.",
    "Your project access: schema, data, SQL and migrations. Can be limited to one project or read-only.",
    ["Create a project at supabase.com.",
     "Add the Supabase connector: + → Connectors.",
     "Say: set up sign-in and a favorites table. Claude designs the tables and runs the migrations.",
     "Claude puts the URL and publishable key in .env. The secret key never goes in the app.",
     "Open the table editor to see the rows.",
     "Rinse and repeat: describe the next change to the data."]))

# ============================================================== 19-20 Railway
slides.append(intro("railway", "19", "Railway", "Hosting and scheduled tasks", "Railway",
    ["Runs services that have to stay up: APIs, workers, databases.",
     "Scheduled tasks, like a nightly data refresh, that Claude sets up and deploys.",
     "Logs and metrics show what happened when a run fails."],
    "set this up as a scheduled task that runs every morning and deploy it to railway",
    shot("railway-canvas.webp", "A Railway project canvas with a card for each service and an activity feed of deploys.", 1295, 695,
         "Each card is a service in the project. The activity feed lists deploys and restarts.", "railway.com", "https://railway.com"),
    ["Run services", "Scheduled tasks", "Databases", "Variables", "Logs and metrics", "Deploy from GitHub"]))
slides.append(setup("railway-setup", "20", "Railway: setup and use.", "Deploy from the repo. Schedule it.", "Railway",
    "Something has to stay running or run on a schedule: an API, a worker, a nightly refresh.",
    "Ask Claude to write the task, set the schedule and read the logs when a run fails. Claude handles the config.",
    "Your project access: deploys, variables and logs.",
    ["Ask: run this every morning and host it on Railway.",
     "Sign in to Railway if it asks. Claude creates the project from the repo.",
     "Claude adds the variables and sets the start command or cron schedule.",
     "Later pushes redeploy automatically.",
     "Ask Claude to check the logs after the first run.",
     "Rinse and repeat: ask for the next change."]))

# ============================================================== 21 one feature
feat = [
    ("Prep the design, wireframe etc", "Components, auto layout, named layers, variables, claude will read it all", ["Figma"]),
    ("Start a session", "Paste the frame link and say what you want. Connectors on.", ["Claude Code"]),
    ("Plan, then build", "Approve the plan, then watch the live preview as it builds.", ["Claude Code"]),
    ("Check against the design", "Ask for every difference from the frame. Fix in small steps.", ["Claude Code", "Figma"]),
    ("Claude opens the PR", "It pushes the branch, opens the PR and watches the checks.", ["GitHub", "Vercel"]),
    ("Claude merges it", "Once checks pass, it merges and Vercel ships it. Then the next feature.", ["GitHub", "Vercel"]),
]
fl = "\n".join(f'''      <li><b>{i}</b><h3>{E(h)}</h3><p>{E(p)}</p>{pills(s, "pills--sm")}</li>''' for i, (h, p, s) in enumerate(feat, 1))
body = f'''    <ol class="feature" data-feature>
{fl}
    </ol>
    <div class="loopbar">
      <button class="btn btn--solid" type="button" data-loop aria-pressed="false">Play the loop</button>
      <p class="note">Add Supabase for real data, Railway for scheduled tasks.</p>
    </div>'''
slides.append(shell("feature", "21", "One feature, start to finish.", "Then rinse and repeat.", "Start to finish", body))

# ============================================================== 22 links
links = [
    ("Claude Code", "code.claude.com/docs", "https://code.claude.com/docs/en/desktop", "Desktop app, worktrees, permission modes"),
    ("Figma", "developers.figma.com/docs/figma-mcp-server", "https://developers.figma.com/docs/figma-mcp-server/", "The MCP server behind the Figma connector"),
    ("GitHub", "docs.github.com", "https://docs.github.com/en/pull-requests", "Pull requests, Pages, Actions"),
    ("Vercel", "vercel.com/docs", "https://vercel.com/docs", "Deployments, previews, environment variables"),
    ("Supabase", "supabase.com/docs", "https://supabase.com/docs", "Database, auth, storage"),
    ("Railway", "docs.railway.com", "https://docs.railway.com", "Services, variables, cron schedules"),
]
lr = "\n".join(f'        <tr><td data-label="Tool">{E(a)}</td><td data-label="Docs"><a href="{u}" target="_blank" rel="noopener">{E(l)}</a></td><td class="muted" data-label="What’s there">{E(d)}</td></tr>' for a, l, u, d in links)
body = f'''    <table class="grid grid--links">
      <thead><tr><th scope="col">Tool</th><th scope="col">Docs</th><th scope="col">What&rsquo;s there</th></tr></thead>
      <tbody>
{lr}
      </tbody>
    </table>
    <div class="credits">
      <p><b>Screens.</b> The Figma editor and Vercel deployments are my own windows. The GitHub, Supabase and Railway images come from each company&rsquo;s public docs and site. The Claude Code video is Anthropic&rsquo;s, on YouTube.</p>
      <p><b>Not affiliated.</b> This page isn&rsquo;t affiliated with or endorsed by Anthropic, Figma, GitHub, Vercel, Supabase, Railway or Wiley. &ldquo;For Dummies&rdquo; is a trademark of John Wiley &amp; Sons, and the cover is shown as a joke about the title.</p>
      <p>Slides were made in Figma. This page was built with Claude Code, by someone who didn&rsquo;t write the code.</p>
    </div>'''
slides.append(shell("links", "22", "Links and docs.", "Where to read more.", "Start to finish", body))

# ---------------------------------------------------------------- cover
cover = f'''
<section class="slide slide--cover" id="cover" data-n="01" data-title="The most powerful dev tools." data-chapter="Start" data-time="{notes["01"]["t"]}">
  <div class="cover">
    <div class="cover__text">
      <h1 class="cover__title"><span><i>The most powerful</i></span><span><i>dev tools.</i></span></h1>
      <p class="cover__sub">As a dummy (Ian), for dummies.</p>
      <div class="cover__go">
        <a class="btn btn--solid" href="#claude-code">Start reading</a>
        <button class="btn" type="button" data-present>Present <kbd>P</kbd></button>
      </div>
    </div>
    <figure class="cover__book"><img src="assets/img/book.webp" alt="The cover of Web Design For Dummies." width="577" height="671" decoding="async"></figure>
    <p class="cover__hint">Scroll, use the nav, or press P to present</p>
  </div>
  <aside class="slide__notes" hidden>{note_html("01")}</aside>
</section>'''

# ---------------------------------------------------------------- nav
chapters = [
    ("Start", "cover", [("cover", "The most powerful dev tools.")]),
    ("Claude Code", "claude-code", [("claude-code", "Build"), ("own-thing", "Its own thing"), ("folders", "Folders and memory"),
                                    ("claude-code-setup", "Setup and use"), ("point", "Point at it"), ("permissions", "Permissions")]),
    ("How it connects", "connects", []),
    ("Figma", "figma", [("figma", "Design"), ("figma-setup", "Setup and use")]),
    ("GitHub", "github", [("github", "Version control"), ("github-ask", "I ask. Claude does."), ("github-terms", "Four terms"), ("github-setup", "Setup and use")]),
    ("Vercel", "vercel", [("vercel", "Deploy"), ("vercel-setup", "Setup and use")]),
    ("Supabase", "supabase", [("supabase", "Data and auth"), ("supabase-setup", "Setup and use")]),
    ("Railway", "railway", [("railway", "Hosting and tasks"), ("railway-setup", "Setup and use")]),
    ("Start to finish", "feature", [("feature", "One feature"), ("links", "Links and docs")]),
]
nav = []
for name, first, kids in chapters:
    if name == "Start":
        kids = []
    li = f'      <li class="chapter" data-chapter="{E(name)}"><a class="chapter__link" href="#{first}">{E(name)}</a>'
    if kids:
        li += '\n        <ul class="branch">\n' + "\n".join(f'          <li><a href="#{i}">{E(t)}</a></li>' for i, t in kids) + "\n        </ul>\n      "
    li += "</li>"
    nav.append(li)
nav_html = "\n".join(nav)

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>The most powerful dev tools. As a dummy, for dummies.</title>
<meta name="description" content="A designer's guide to Claude Code and the tools it connects to: Figma, GitHub, Vercel, Supabase and Railway. You describe the outcome. Claude does the code, git and deploys.">
<meta name="theme-color" content="#191919">
<meta property="og:type" content="website">
<meta property="og:title" content="The most powerful dev tools. As a dummy, for dummies.">
<meta property="og:description" content="A designer's guide to Claude Code, Figma, GitHub, Vercel, Supabase and Railway.">
<meta name="twitter:card" content="summary">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;700&family=Geist+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to the slides</a>
<div class="progress" aria-hidden="true"><span class="progress__bar" data-progress></span></div>

<header class="topbar">
  <button class="btn" type="button" data-menu aria-expanded="false" aria-controls="rail">Menu</button>
  <div class="topbar__now" aria-live="polite"><b data-now-title>The most powerful dev tools.</b><span data-now-count>01 / {TOTAL}</span></div>
  <button class="btn btn--solid" type="button" data-present>Present</button>
</header>
<div class="scrim" data-scrim></div>

<nav class="rail" id="rail" aria-label="Slides">
  <a class="rail__brand" href="#cover">The most powerful dev tools.<span>As a dummy, for dummies.</span></a>
  <div class="rail__actions">
    <button class="btn btn--solid" type="button" data-present>Present <kbd>P</kbd></button>
    <button class="btn" type="button" data-keys>Keys <kbd>?</kbd></button>
  </div>
  <div class="graph" data-graph>
    <span class="graph__progress" data-graph-progress></span>
    <ol class="chapters">
{nav_html}
    </ol>
  </div>
  <p class="rail__foot">22 slides, about 30 minutes.<br>Slides from Figma. Page built with Claude Code.</p>
</nav>

<main id="main">
{cover}
{"".join(slides)}
</main>

<div class="hud" role="group" aria-label="Presenter controls">
  <span><b data-hud-n>01</b> / {TOTAL}</span>
  <span>Slide <b data-hud-slide>0:00</b> of <span data-hud-budget>0:30</span></span>
  <span>Total <b data-hud-total>0:00</b> of 30:00</span>
  <button class="btn" type="button" data-timer>Pause</button>
  <button class="btn" type="button" data-reset-clock>Reset</button>
  <button class="btn" type="button" data-notes-toggle>Notes <kbd>N</kbd></button>
  <button class="btn" type="button" data-fs>Fullscreen <kbd>F</kbd></button>
  <button class="btn btn--solid" type="button" data-present>Exit <kbd>Esc</kbd></button>
</div>

<aside class="notes" aria-label="Speaker notes" data-notes>
  <div class="notes__in">
    <p class="notes__meta"><span data-notes-title></span><span data-notes-time></span></p>
    <div data-notes-body></div>
    <p class="notes__next" data-notes-next></p>
  </div>
</aside>

<div class="keys" data-keys-modal role="dialog" aria-modal="true" aria-label="Keyboard shortcuts">
  <div class="keys__box">
    <h2>Presenting</h2>
    <dl>
      <dt><kbd>P</kbd></dt><dd>Start or stop presenting</dd>
      <dt><kbd>&rarr;</kbd> <kbd>Space</kbd> <kbd>J</kbd></dt><dd>Next slide</dd>
      <dt><kbd>&larr;</kbd> <kbd>K</kbd></dt><dd>Previous slide</dd>
      <dt><kbd>Home</kbd> <kbd>End</kbd></dt><dd>First or last slide</dd>
      <dt><kbd>N</kbd></dt><dd>Speaker notes</dd>
      <dt><kbd>F</kbd></dt><dd>Fullscreen</dd>
      <dt><kbd>?</kbd></dt><dd>This list</dd>
      <dt><kbd>Esc</kbd></dt><dd>Close this, or stop presenting</dd>
    </dl>
    <p class="note" style="margin-top:16px">Outside presenting, <kbd>J</kbd> and <kbd>K</kbd> still jump slide to slide.</p>
  </div>
</div>

<script src="assets/app.js" defer></script>
</body>
</html>
'''
(SITE / "index.html").write_text(page, encoding="utf-8")
print("wrote", SITE / "index.html", len(page), "bytes")
