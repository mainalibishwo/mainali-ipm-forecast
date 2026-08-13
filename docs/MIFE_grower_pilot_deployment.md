# MIFE grower-pilot deployment

## Release boundary

This release is a research-based decision-support pilot. It reports relative
population phenology, a nine-scenario sensitivity envelope, crop-stage overlap
and an optional sampling-equivalent field density. It does not report an
economic threshold or pesticide recommendation.

The frozen biological parameter files must not be edited during deployment.

## Recommended architecture

1. GitHub `main` is the versioned source and rollback history.
2. A persistent Docker web service runs the FastAPI application.
3. Cloudflare DNS maps `forecast.mainaliipm.com` to the service's verified
   custom-domain target and provides TLS and edge protection.
4. The service health check is `GET /health`.

The initial pilot uses Render's Free web-service instance. It may spin down
after inactivity and the first returning visitor may experience a cold-start
delay. Upgrade the hosting instance when usage or availability expectations
increase; this does not require charging growers or changing MIFE biology.

The repository includes a non-root production `Dockerfile`. Only runtime files
needed by the dashboard are copied into the image. Research outputs, tests,
backups and bundle-transfer files are excluded.

## Release checks

Before every deployment:

```bash
python -m pytest -q
git status --short
git log -1 --oneline
```

Expected for this checkpoint: 51 passing tests and a clean worktree after the
deployment commit.

After deployment, verify:

1. `/health` returns status `ok`.
2. The location list distinguishes validation and regional series.
3. Malua, Knockrow and Dorey cannot select live weather.
4. A numbered regional series completes all nine live-weather scenarios.
5. Stored mode produces a reproducible historical run.
6. The field estimator calculates 31.25 sampling-equivalent bugs/ha for 3 bugs,
   30 sampled trees and 8 m by 4 m spacing.
7. Desktop and mobile layouts display the scientific qualification text.

## Cloudflare hostname

Use `forecast.mainaliipm.com`. Add the hostname first in the origin hosting
service, wait for its verification target, then create the exact CNAME supplied
by that service in Cloudflare DNS. Keep the record proxied unless the hosting
service explicitly requires DNS-only during verification.

Do not point the production hostname to a Codespaces forwarded port. A
Codespace is a development environment and can stop independently of growers.

## Rollback

If a release fails, redeploy the previous known-good Git commit rather than
editing biological inputs in production. The current pre-deployment rollback
checkpoint is `cf66cef`; the complete dashboard checkpoint before production
packaging is `bbea65d`.
