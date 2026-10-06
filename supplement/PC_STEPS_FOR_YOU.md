# AAMAS 2027 experiments: what to do on the PC (Docker)

The measured run uses exactly the anonymized supplementary material we ship: `krrood-aamas27-supplement.zip`. It
contains all the code, the data, the Docker set-up and `reproduce.sh`. The script `pc_run.sh` does all the set-up
steps on the PC. A Claude Code session on the PC can follow this file too: it must not change any file of the
bundle, must not change the limits or repetitions, and must stop and report if a step fails.

## 1. Before you start (5 minutes)

1. Turn on the PC, log in, and plug in the power cable. Close everything (GraphDB Desktop, Protégé, PyCharm,
   browser).
2. Download the two files from the Claude conversation into `~/Downloads` (or copy them by USB stick):
   `krrood-aamas27-supplement.zip` and `pc_run.sh`.

## 2. Set up and start the run (one command, 15-20 minutes until it runs on its own)

```bash
bash ~/Downloads/pc_run.sh
```

It asks for your password once if it has to install something. It then:

1. installs Docker from Ubuntu's packages (`docker.io`, `docker-compose-v2`) if needed, not the snap, which can't
   read `~/.graphdb`;
2. adds you to the `docker` group and continues with that group active, so you don't need to log out;
3. finds the GraphDB license (`~/.graphdb/work/graphdb.license`, `~/graphdb.license`, `~/Downloads/graphdb.license`,
   else any `*.license` file with "graphdb" in its name or folder under `~`, `/opt` and `/etc`) and the zip (`~` or
   `~/Downloads`), and checks for 15 GB of free disk;
4. unzips the bundle into `~/krrood-aamas27-supplement`, replacing an earlier bundle there but keeping its `state/`
   folder with results, and prints the BUNDLE id: **write it down**;
5. builds the Docker image (5-10 min), checks that the image holds the zip's code (same BUNDLE id), runs the listing tests (expected: `24 passed`, then `1 passed`), and starts
   GraphDB once with the license to check that GraphDB accepts it;
6. records the PC's details in `state/results/aamas27/run/host/host.json`: CPU, frequency governor, turbo, power
   profile, RAM, disk, board, OS, kernel and Docker version (no hostname or user name, since the results are
   shipped anonymized);
7. starts the full run in the background, blocks suspend while it runs, and waits until GraphDB has started;
8. starts a monitor that writes every 30 s to `host/monitor.csv`: load, memory and swap, mean CPU frequency, maximum
   temperature, and the programs outside Docker that used at least 5 % of a CPU (`busy_outside_docker`, which
   should stay empty). It stops when the run ends.

When it prints **"The run is going"**, leave the PC alone until tomorrow (about 9-13 hours): screen lock is fine,
but don't log out, and don't use the PC. These are the timings for the paper.

If it stops with an error, read the message: it says what is missing (license, zip, disk space) or shows the end of
the log. After fixing it, run the same command again. It never starts a second run while one is going, and a
stopped run resumes after its last finished step.

### If it says "No GraphDB license file found"

GraphDB 11 needs a license file, even the free edition. Save the license file `graphdb.license` from the Claude
conversation (the laptop's license) as `~/.graphdb/work/graphdb.license`:

```bash
mkdir -p ~/.graphdb/work && cp ~/Downloads/graphdb.license ~/.graphdb/work/graphdb.license
```

Or request a free license on the GraphDB website and save it there. If the license is somewhere else, run
`GRAPHDB_LICENSE=/path/to/file.license bash ~/Downloads/pc_run.sh`. If GraphDB rejects the license, the script stops
and shows GraphDB's answer.

### If Docker says "permission denied"

Adding you to the `docker` group (`sudo usermod -aG docker $USER`) only takes effect for new logins. The script
works around this by continuing with `sg docker`. If it still ends with "Docker still says permission denied":

* **Recommended:** log out of the desktop session and log back in (or reboot), open a new terminal, and run
  `bash ~/Downloads/pc_run.sh` again.
* **Or, in this terminal only:** run `newgrp docker`, then `bash ~/Downloads/pc_run.sh` in that same terminal. Other
  terminals don't have the group until you log out and back in.

If it persists after logging back in, check `groups | grep -w docker || echo "not in docker group"`. If it prints
"not in docker group", run `sudo usermod -aG docker $USER` again, then log out and back in.

## 3. Check on it (any time)

```bash
bash ~/Downloads/pc_run.sh status
```

It shows whether the run is going, the finished steps, the last samples of the monitor, and the end of the log
(`~/krrood-aamas27-supplement/state/reproduce.log`).

## 4. When it's finished (next morning)

`status` shows `No run is going`, and the log ends with `finished mode all`. Check in
`~/krrood-aamas27-supplement/state/reproduce.log`:

- `24 passed` (tests), and `24 passed` / `1 passed` (listings);
- after `start answer_check`: every system `status=ok`, and the step finished (it fails on any difference);
- after `start soundness_audit`: `individuals 3667 3667`; classes 17558 / 17558 / unsound 0 / missing 0;
  object properties 1385869 / 1385869 / 0 / 0; data properties 20933 / 20933 / 0 / 0;
  `passed: True, equalities: 0, inconsistencies: 0`.

## 5. Protégé, by hand (about 1 hour)

On the PC itself (not in Docker), with nothing else running:

1. Install the Pellet plug-in and "Snap SPARQL Query" once (File -> Check for plugins), and set
   `max_heap_size=28G` in `~/.Protege/conf/jvm.conf`.
2. For the raw file `~/krrood-aamas27-supplement/code/earlier/experiments/resources/owl2bench_statements_unreasoned.rdf`
   and then the reasoned file `~/krrood-aamas27-supplement/state/owl2bench_statements_reasoned.rdf`, start a fresh
   Protégé with `/usr/bin/time -v -o ~/protege_raw_time.txt ./run.sh` (`protege_reasoned_time.txt` for the second
   file), open the file, select Reasoner -> Pellet, Reasoner -> Start reasoner, note the loading and reasoning time
   from the log, and quit.
3. In a new session on the reasoned file, Start reasoner, then run the 18 SPARQL queries of
   `~/krrood-aamas27-supplement/code/earlier/experiments/src/krrood_experiments/owl2bench/sparql_queries.py` in Snap
   SPARQL. Note the time and number of results; stop a query after 60 s ("timeout").
4. Fill in `~/krrood-aamas27-supplement/code/earlier/experiments/scripts/aamas27/protege_template.json` and save it
   as `~/krrood-aamas27-supplement/state/results/aamas27/run/protege.json`. Then:

   ```bash
   bash ~/Downloads/pc_run.sh tables
   ```

## 6. Hand back (one file)

Everything the paper needs is in one file: `~/krrood-aamas27-supplement/state/aamas27_results.tgz` (the
measurements, the checks, the LaTeX tables, Protégé's numbers and the PC's details).

Easiest: upload it to your Google Drive in the browser on the PC, and tell the paper session its name. The session
fetches it, checks it, and puts the tables into the paper (`planning/import_results.sh`). Or copy it by USB stick
into `~/Projects/krrood_aamas/planning/` on the laptop. The session then writes the "[TBD]" paragraphs, builds the
final supplementary zip with the results, and rebuilds the PDF.

## Appendix: the same steps by hand

Only if the script can't be used.

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2 unzip
sudo usermod -aG docker $USER          # then log out and back in
docker compose version && docker run --rm hello-world > /dev/null && echo "docker ok without sudo"
cd ~ && unzip -q -o -DD ~/Downloads/krrood-aamas27-supplement.zip && cd krrood-aamas27-supplement && mkdir -p state
# -DD: files get the current time; without it Docker can build the image from an earlier bundle's files
cat environment/BUNDLE
export GRAPHDB_LICENSE=~/.graphdb/work/graphdb.license
docker compose build
docker run --rm krrood-aamas27 fingerprint   # must print the same id as environment/BUNDLE
docker run --rm krrood-aamas27 listings
nohup systemd-inhibit --what=sleep:idle --why="AAMAS27 experiments" \
    docker compose run --rm -T experiments all > ~/aamas27_run.log 2>&1 &
tail -f state/reproduce.log            # Ctrl+C stops watching, not the run
# after Protégé:
docker compose run --rm -T experiments tables && docker compose down
```
