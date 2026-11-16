# VHS tape for a ~30s terminal GIF of the CPU quickstart.
# Render from the repository root, with the stack already built:
#   vhs examples/quickstart/quickstart.tape
#
# The output path is /workspace/promo/quickstart.gif when this file is
# copied there, or examples/quickstart/quickstart.gif in the repo.
# This tape assumes the working directory is examples/quickstart and
# that images are already pulled, so the recording shows compose up
# and the first MCP query rather than a multi-minute image build.

Output examples/quickstart/quickstart.gif
Set Shell bash
Set FontSize 16
Set Width 1200
Set Height 700
Set Padding 12
Set Theme "Catppuccin Mocha"
Set PlaybackSpeed 1
Set TypingSpeed 40ms

Hide
Type "cd examples/quickstart"
Enter
Sleep 300ms
Show

Type "docker compose up --build -d"
Enter
Sleep 8s

Type "docker compose logs app --tail 20"
Enter
Sleep 3s

Type "docker compose exec app python examples/quickstart/query.py \"how is the discount calculated?\""
Enter
Sleep 8s

Sleep 2s
