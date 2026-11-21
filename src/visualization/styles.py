"""CSS restrito a classes próprias e à classe pública de st.container(key=...)."""

CSS = """
<style>
@font-face {font-family:Inter;src:url("app/static/fonts/inter-variable.ttf") format("truetype");
  font-style:normal;font-weight:100 900;font-display:swap;}
@font-face {font-family:"Source Serif 4";
  src:url("app/static/fonts/source-serif-4-variable.ttf") format("truetype");
  font-style:normal;font-weight:200 900;font-display:swap;}
.oh-section-title {font:600 clamp(1.6rem,3vw,2rem)/1.25 "Source Serif 4",Georgia,serif;
  letter-spacing:-.015em;margin:1.6rem 0 .6rem;}

.oh-brand {display:flex;justify-content:space-between;align-items:center;gap:1rem;
  border-top:3px solid #8B342F;border-bottom:1px solid #DDD8D0;padding:1.05rem 0;
  color:#171717;font:600 .84rem/1.5 Inter,Arial,sans-serif;}
.oh-brand-name {display:block;max-width:36ch;letter-spacing:.015em;}
.oh-brand-meta {text-align:right;color:#626262;font-size:.76rem;font-weight:400;}
.oh-kicker {margin:1.4rem 0 .25rem;color:#8B342F;font:600 .74rem/1.5 Inter,Arial,sans-serif;
  letter-spacing:.13em;text-transform:uppercase;}
.st-key-page_heading h1 {font-family:"Source Serif 4",Georgia,serif;
  font-weight:600;font-size:clamp(2.25rem,5vw,4.15rem);line-height:1.08;
  max-width:24ch;letter-spacing:-.025em;padding-bottom:.5rem;}
.oh-intro {display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);
  gap:2.5rem;padding:.3rem 0 1.5rem;border-bottom:1px solid #DDD8D0;}
.oh-intro p {font-size:1.05rem;line-height:1.8;margin:0;max-width:70ch;}
.oh-intro .oh-deck {font-size:1.25rem;line-height:1.55;margin-bottom:1rem;}
.oh-context {border-left:2px solid #DDD8D0;padding-left:1.2rem;
  color:#626262;font:400 .84rem/1.8 Inter,Arial,sans-serif;}
.oh-context strong {color:#171717;font-weight:600;}
.oh-kpi-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;
  margin:.5rem 0 1rem;}
.oh-kpi {background:#FFFFFF;border:1px solid #DDD8D0;border-top:3px solid #47635C;
  padding:1.3rem;display:flex;flex-direction:column;min-height:19rem;border-radius:3px;min-width:0;}
.oh-kpi h3 {font:600 .9rem/1.5 Inter,Arial,sans-serif;margin:0;min-height:2.7rem;}
.oh-kpi-value {font:500 clamp(1.85rem,3vw,2.55rem)/1.2 Inter,Arial,sans-serif;
  font-variant-numeric:tabular-nums;letter-spacing:-.04em;margin:.65rem 0 .2rem;}
.oh-kpi-unit {font-size:.78rem;color:#626262;margin:0 0 .7rem;}
.oh-kpi-context {font-size:.85rem;line-height:1.6;margin:0 0 1rem;}
.oh-kpi-meta {margin-top:auto;border-top:1px solid #DDD8D0;padding-top:.7rem;
  font-size:.8rem;line-height:1.65;color:#626262;overflow-wrap:anywhere;}
.oh-status {display:inline-block;color:#6B2825;background:#F3E7DD;
  padding:.18rem .5rem;border-radius:3px;font:500 .72rem/1.5 Inter,Arial,sans-serif;
  margin-top:.5rem;}
.oh-status-exploratory,.oh-status-verified {color:#355449;background:#EAF0EA;}
.oh-status-unavailable {color:#56524B;background:#EAE5DC;}
.oh-note {border-left:3px solid #47635C;background:#EAE5DC;padding:1rem 1.2rem;margin:.5rem 0 1rem;
  font-size:.88rem;line-height:1.7;}
.oh-note strong {display:block;font-weight:600;margin-bottom:.2rem;}
.oh-note-exploratory {border-color:#8B342F;}
.oh-section-description {color:#626262;max-width:78ch;font-size:.95rem;
  line-height:1.75;margin:0 0 .8rem;}
.oh-reading {border-top:1px solid #DDD8D0;padding-top:1rem;font-size:.92rem;line-height:1.75;}
.oh-reading strong {color:#47635C;}
.oh-explore-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
  gap:1rem;margin:.6rem 0 1.4rem;}
.oh-explore {display:block;color:#171717;text-decoration:none;background:#FFFFFF;
  border:1px solid #DDD8D0;padding:1.4rem;min-height:10rem;border-radius:3px;}
.oh-explore:hover {border-color:#8B342F;}
.oh-explore h3 {font:600 1.2rem/1.4 'Source Serif 4',Georgia,serif;margin:0 0 .65rem;}
.oh-explore p {color:#626262;font-size:.85rem;line-height:1.65;margin:0;}
.oh-explore span {display:block;color:#8B342F;font-size:.8rem;font-weight:600;margin-top:.8rem;}
.oh-document {padding:1.2rem 0;border-bottom:1px solid #DDD8D0;}
.oh-document h3 {font:600 1.2rem/1.4 'Source Serif 4',Georgia,serif;margin:.2rem 0 .5rem;}
.oh-document p,.oh-document a {font-size:.85rem;line-height:1.6;}
.oh-document a {color:#8B342F;text-decoration:underline;text-underline-offset:.2em;}
.oh-document-meta {color:#626262;font-size:.78rem;}
.oh-source {background:#FFFFFF;border:1px solid #DDD8D0;padding:1.2rem;margin:.6rem 0;}
.oh-source h3 {font:600 1.1rem/1.5 'Source Serif 4',Georgia,serif;margin:0 0 .5rem;}
.oh-source p {font-size:.84rem;line-height:1.7;margin:.2rem 0;overflow-wrap:anywhere;}
.oh-source a {color:#8B342F;text-decoration:underline;}
.oh-footer {border-top:1px solid #DDD8D0;margin-top:2rem;padding:1.2rem 0;
  font-size:.78rem;line-height:1.8;color:#626262;}
.oh-explore:focus-visible,.oh-document a:focus-visible,.oh-source a:focus-visible {
  outline:3px solid #8B342F;outline-offset:4px;}
@media(max-width:1000px) {
  .oh-kpi-grid,.oh-explore-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
  .oh-kpi {min-height:18rem;}
}
@media(max-width:600px) {
  .oh-brand {align-items:flex-start;}
  .oh-brand-meta {max-width:16ch;font-size:.68rem;}
  .oh-intro {grid-template-columns:1fr;gap:1.3rem;}
  .oh-intro p {font-size:1rem;}
  .oh-intro .oh-deck {font-size:1.1rem;}
  .oh-kpi-grid,.oh-explore-grid {grid-template-columns:1fr;}
  .oh-kpi {min-height:0;padding:1.15rem;}
  .oh-kpi h3 {min-height:0;}
  .oh-kpi-value {font-size:2.3rem;}
}
</style>
"""
