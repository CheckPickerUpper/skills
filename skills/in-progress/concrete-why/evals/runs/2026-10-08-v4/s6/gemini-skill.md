Checking stamina inside the ability means the ability either misses when stamina runs out mid-attack, or it has to check the number every frame. Keep the tag, so the tag container can notify the ability the moment it needs to stop.

**How abilities and attributes notify changes**

An ability's `Gate` (the condition for both starting and continuing) depends on tags. The rules for how abilities run are in `ADR 0005` (`docs/adr/0005-an-ability-is-asked-for-and-ends-only-as-declared.md`), which states that abilities watch the tag container. The rules for attributes like stamina are in `ADR 0003` (`docs/adr/0003-a-mutation-returns-its-change.md`), which states that nothing subscribes to attributes.

```ts
// docs/adr/0005-an-ability-is-asked-for-and-ends-only-as-declared.md:101
// Re-asking every ability's condition every tick is watching a symptom. The tag container knows the
// moment a tag changes and reports it. An active ability is told directly by the tag container when
// a tag it depends on changes...
```

```ts
// docs/adr/0003-a-mutation-returns-its-change.md:47
// GameplayAttributeContainer already works this way — every mutation hands back a
// GameplayAttributeChange, and nothing subscribes to attributes.
```
// ▸ An ability cannot be told when stamina reaches 0, because attribute changes do not notify listeners.

**What checking stamina inside Hora's Flurry breaks**

*1. Hora's Flurry never stops when it empties the stamina bar mid-attack.*

Hora's Flurry is a continuous ability that drains stamina while running.

```ts
// Illustration, not the real code
if (attributes.Read(Stamina) === 0) {
    return { Kind: "Refused" };
}
// ▸ This only prevents the ability from starting.
```

1. A player starts Hora's Flurry with low stamina.
2. The initial `stamina === 0` check passes, and the flurry begins.
3. The flurry drains stamina each frame until stamina hits 0.
4. Because the ability isn't polling, and attributes have no subscribers, Hora's Flurry doesn't know stamina is gone.
5. The player keeps flurrying with 0 stamina.

If exhaustion is a tag, whatever drains the stamina grants the tag when stamina hits 0. The tag container immediately tells Hora's Flurry "a tag you depend on changed." The ability re-evaluates its `Gate`, sees the blocker, and ends itself.

*2. Every stamina-using ability writes the same check.*

Sprint and dodge are other abilities that require stamina to start.

1. The player's stamina hits 0.
2. They try to Sprint or Dodge.
3. If exhaustion is not a tag, every single ability that requires stamina has to read the stamina attribute itself to refuse activation.
4. With a tag, every stamina-using ability simply names the tag in its `Gate` declaration, and the engine handles refusing the activation.

**What I couldn't confirm:** I could not find the exact path of Hora's Flurry or the exact name of the exhaustion tag (e.g., `Status.Exhausted`), because a sandbox connection error in this session prevented grepping the codebase for the exact spelling.

**What decides it:** Can the ability system react to a resource emptying mid-channel without polling every frame? A tag pushes a notification; a raw attribute check requires polling.
