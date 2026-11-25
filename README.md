# priyanka36.github.io

Personal academic website of **Priyanka Paudel**, PhD student. Live at <https://priyanka36.github.io>.

Built with [Jekyll](https://jekyllrb.com/) using a small custom layout (no external theme), hosted on GitHub Pages.

## Where to edit

| What | File |
| --- | --- |
| Bio, research interests, education, teaching, experience | `_pages/about.md` |
| News items | `_data/news.yml` |
| Publications (set `selected: true` to show on home page) | `_data/publications.yml` |
| Name, title, photo, header links | `_config.yml` (`author:`) |
| Styling | `assets/css/main.css` |
| Top menu | `_data/navigation.yml` |
| CV | edit `_cv/cv.html`, then run `bash _cv/build.sh` to regenerate `assets/Documents/Paudel_Priyanka_CV.pdf` |
| Projects (shown on /projects/) | `_posts/` with `categories: [Projects]` |
| Blog | `_pages/blogs.md` |

## Run locally

```bash
bundle install
bundle exec jekyll serve
# open http://localhost:4000
```
