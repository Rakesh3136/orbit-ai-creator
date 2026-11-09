# AIMN portability and migration

AIMN must remain movable between a personal computer, another computer, a VPS, or a future hosting provider. GitHub is the source-code home, not a runtime requirement.

## Portability contract

- **Runtime:** Docker Compose; build containers from this repository so the same application stack can run on supported Docker hosts.
- **Configuration:** all machine-specific settings and credentials come from environment variables in a private `.env`. Never commit `.env`, OAuth client files, tokens, or passwords.
- **Database:** PostgreSQL data lives in the named `aimn_postgres_data` Docker volume. Use logical database dumps for migration rather than copying a live database volume between different Docker hosts.
- **Application state:** keep user-created media, generated assets, and agent memory in explicit persistent data directories/volumes as those features are integrated. Do not treat a container's writable layer as durable storage.
- **AI runtime:** keep model/provider selection behind configuration and adapter interfaces. A model change must not require changing task, memory, or channel data formats.
- **Integrations:** keep provider credentials and provider-specific code behind adapters. A hosting move must not require reconnecting or exposing secrets in source control.
- **Control plane:** GitHub Actions may test and package AIMN, but AIMN must still be runnable without GitHub Actions.

## Move AIMN to another computer

### 1. Prepare a safe backup on the current computer

From the repository root:

```bash
mkdir -p backups
docker compose exec -T postgres pg_dump -U aimn -d aimn -Fc > backups/aimn-$(date +%Y%m%d-%H%M%S).dump
```

Check that the dump file exists and is not empty. Keep a secure copy of the private `.env` separately. It contains the owner password hash and server secrets. Transfer it using a trusted encrypted method; do not upload it to GitHub or send it in chat.

Also back up any user media, generated assets, or other persistent directories that your deployment uses. The current Compose file defines the PostgreSQL volume; it does not yet define a dedicated shared media volume. Check the current deployment's configured paths before moving media.

### 2. Prepare the new computer

1. Install Docker Engine + the Docker Compose plugin, or Docker Desktop.
2. Clone this repository (or download a release/archive) on the new computer.
3. Transfer the private `.env` file into the repository root using a secure method.
4. Transfer the database dump and any persistent media/asset backups.
5. Start the database service:

```bash
docker compose up -d postgres
docker compose ps
```

### 3. Restore the database

Restore only into an empty AIMN database. This command replaces objects in the target database; verify the target and keep the original backup before running it.

```bash
docker compose exec -T postgres pg_restore -U aimn -d aimn --no-owner --no-privileges --clean --if-exists < backups/aimn-backup.dump
```

If the dump was created under a different filename, replace `backups/aimn-backup.dump` with its actual path. Do not run a restore against a database containing data you need to preserve.

### 4. Start AIMN and verify

```bash
docker compose up --build -d
docker compose ps
docker compose logs --tail=100 api worker web
```

Open `http://localhost:3000`, sign in with the owner account, and verify networks, channels, tasks, approvals, and agent lessons. Verify media files separately if your deployment uses them.

## Moving between hosting providers

- Build and run the same Compose services on the new host.
- Transfer the private configuration and database backup securely.
- Set `AIMN_WEB_ORIGIN` to the new public HTTPS origin and keep `AIMN_SESSION_COOKIE_SECURE=true` for HTTPS.
- Configure TLS/reverse proxying on the new host. Do not publish PostgreSQL or the private API directly to the internet.
- Update OAuth redirect URIs with the provider's console when the public callback URL changes; keep OAuth client secrets out of Git.
- Test login, database migrations, background worker health, backups, and restore before switching users to the new host.
- Keep the old host and its backup intact until the new deployment has been verified.

## Current limitations

This is a migration procedure for the current Docker Compose foundation, not a claim that every AIMN subsystem is already production-ready. Automated backup scheduling, dedicated media/object storage migration, restore drills, multi-host orchestration, and seamless zero-downtime cutover are future work. The current AI worker is deterministic; portability does not imply autonomous model training or unlimited free compute.
