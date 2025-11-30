# UART-Protokoll
**Kommunikationsschnittstelle zwischen dem IT-Programm auf dem `Raspberry Pi` und dem ET-Programm auf dem `TinyMK`**

## Nachrichtenformat
Eine Nachricht ist ein String, der durch `\0` abgeschlossen wird.

Die Parameter werden mit `|` getrennt.

Der erste Parameter ist obligatorisch und gibt den Instruktionstyp an.

Die folgenden Parameter *(0..\*)* besitzen einen Namen und einen Wert, getrennt durch `=`.

Da für diese Lösung nur ganzzahlige numerische Werte benötigt werden, ist kein spezielles Parsing-Format erforderlich.

Die finale Syntax lautet:
```
<type>(|<name=value>*)\0
```

## Nachrichten
**Hier sind die Nachrichten, die für den vollständigen Programmablauf verwendet werden**

| Typ | Sender | Beschreibung | Parameter | Beispiel |
| :-- | :-- | :-- | :-- | :-- |
| Ready | ET | Robot is ready for instructions | - | `ready\0`|
| Reset | IT | Positioniert das System in den Ausgangpunkt. | - | `reset\0` |
| Move | IT | Positioniert und rotiert den Greifer zu den absoluten Koordinaten. Die Position wird in Mikrometer und die Rotation in Grad übergeben (damit eine es als Ganzzahl genau genug ist). | x: uint32, y: uint32, rot: uint32 | `move\|x=123456\|y=32089\|rot=240\0` |
| Pick | IT | Greifen des Puzzleteils. | - | `pick\0` |
| Place | IT | Plaziert das Puzzleteil. | - | `place\0` |
| Finish | IT | Hinweis, dass das Puzzle gelöst ist | - | `finish\0` |
| Error | ET | Robot ran into error | - | `error\0`|
