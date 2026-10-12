# One finding, two items

Job: "The owner opens this to decide whether the character body cleanup is
worth doing." The reader said they were tired and wanted no extraneous load.

## Bare prose

Plain words with the code removed. The heading is a figure of speech, the
reader cannot check the claim, and nothing says why it matters.

```text
Anything that can read a body can also end it

What is wrong    When code asks for a player's body it gets the whole thing,
                 including the buttons for "despawned" and "died".
Could cause      Bugs later.
Fix              Give readers a smaller view.
```

## Full item

The heading is the literal fact and names the method. The real lines sit
beside it with the offending ones marked, then one concrete case of harm, then
what the fix stops compiling. It is longer and easier to read, because every
line is one the reader uses.

```text
`ReadBody()` returns an object that includes the methods that kill and despawn the body

src/Shared/Character/Body.ts:41
  41   ReadBody(player: Player): CharacterBody {      ← every caller gets all of this
  58     Despawn(): void                              ← marked: a reader can call it
  59     Die(): void                                  ← marked: a reader can call it

Example of the bug this allows
  The stamina bar reads the body to show a number. A typo calls `Die()` there
  and the player dies when the HUD opens. Nothing refuses it today.

Becomes
  41   ReadBody(player: Player): CharacterBodyView {  ← position, health, stamina only

After the fix this no longer compiles
  body.Die()       Property 'Die' does not exist on type 'CharacterBodyView'

Status: not built · #412                                        ▸ all 14 callers
```

On the published page the code lines are syntax-coloured, the marked lines
have a tinted background, and `ReadBody()` in the heading has its own colour
and background so it reads as a code name.
