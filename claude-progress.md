# Development Progress

## Current Theme: Ben 10 / Omnitrix

- **Colors**: Omnitrix Green (`#10B981`), Energy Glow (`#00FF88`), Dark tech background
- **Logo**: Custom Omnitrix hourglass SVG component
- **Background**: Green energy grid with pulsing Omnitrix glow
- **Navigation**: Plumber HQ, New Transform, Alien Scan, Alien Database, Omnitrix Alert, Plumber Tech, Grandpa Max
- **Terminology**: Wielder, Transforms, Alien Scans, Villains, DNA Code, "It's Hero Time!"
- **Root Title**: "Omnitrix IP — Tennyson Patents"

## Notifications System
- Backend API: Full CRUD at `/api/v1/notifications/`
- Frontend page: `/dashboard/notifications` (needs Ben 10 color update)
- API client: `frontend/src/lib/api/notifications.ts`

## Architecture
- `frontend/src/components/ui/OmnitrixLogo.tsx` — Omnitrix hourglass logo
- `.omnitrix-bg`, `.energy-grid`, `.omni-glow` CSS background classes
- Omnitrix colors: `omnitrix-green/glow/dark/black/gray/silver`, `alienTech`, `omniGlow`
