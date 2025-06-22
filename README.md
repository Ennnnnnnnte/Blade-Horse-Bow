# Blade Horse Bow - Medieval Turn-Based Strategy Game

Ein mittelalterliches rundenbasiertes Strategiespiel mit drei Einheitentypen: Swordsman, Archer und Rider.

## Features

### Spielmodi
- **Singleplayer**: Spiel gegen KI mit drei Schwierigkeitsgraden
- **Multiplayer**: Spiel gegen einen anderen Spieler

### KI-Schwierigkeitsgrade
- **Leicht**: KI macht zufällige Züge
- **Mittel**: KI verwendet grundlegende Strategien (Empfohlen für Anfänger)
- **Schwer**: KI verwendet komplexe Strategien mit Positionierung und Einheitenpaarungen

### Einheiten
- **Swordsman**: Nahkampf-Einheit mit Lanze (Reichweite 2), Schild-Fähigkeit
- **Archer**: Fernkampf-Einheit mit Bogen (Reichweite 6), Pfeilregen-Fähigkeit
- **Rider**: Schnelle Einheit mit Sturmangriff-Fähigkeit

### Spezialfähigkeiten
- **Swordsman**: Schild hoch - Halbiert erlittenen Schaden für 1 Angriff
- **Archer**: Pfeilregen - Trifft Ziel und alle angrenzenden Felder (3x3 Bereich)
- **Rider**: Sturmangriff - Bewegt sich unbegrenzte Distanz und greift an

### Terrain-System
Das Spiel verfügt über verschiedene Spielfeld-Modifikatoren:

#### 1. Berg (Grau mit X)
- **Unpassierbar**: Einheiten können Berge nicht betreten
- **Blockiert Bewegung**: Berge versperren die Bewegung wie andere Einheiten
- **Blockiert Sichtlinie**: Pfeile können nicht durch Berge geschossen werden

#### 2. Gewässer/Sumpf (Blau)
- **Verlangsamt Bewegung**: Reduziert Bewegungsreichweite um 1 Feld
- **Pferde**: Werden um 2 Felder eingeschränkt
- **Bogenschützen**: Können Gewässer nicht betreten

#### 3. Wald (Grün)
- **Verteidigungsbonus**: Einheiten in Wäldern erhalten nur 3/4 des Schadens (25% weniger)

#### 4. Heilquelle (Hellblau mit +)
- **Heilung**: Einheiten werden um 15% ihrer max HP geheilt beim Betreten

### Spielmechaniken
- **Bewegung**: Realistische Bewegung mit orthogonalen und diagonalen Reichweiten
- **Pfadfindung**: Einheiten können nicht über andere springen
- **Angriffe**: Diagonale Angriffe möglich, verschiedene Reichweiten
- **Sichtlinie**: Bogenschützen benötigen freie Sichtlinie für Angriffe
- **Einheitenpaarungen**: Verschiedene Einheiten sind gegen andere stärker/schwächer

## Installation

1. Stelle sicher, dass Python 3.x installiert ist
2. Installiere Pygame: `pip install pygame`
3. Führe das Spiel aus: `python3 main_gui.py`

## Steuerung

- **Mausklick**: Einheit auswählen, bewegen, angreifen
- **UI-Buttons**: Angriff und Spezialfähigkeiten aktivieren
- **ESC**: Pause-Menü öffnen/schließen

## Spielziel

Besiege alle gegnerischen Einheiten, um zu gewinnen!

## KI-Strategien

Die KI verwendet verschiedene Strategien je nach Schwierigkeitsgrad:

### Leicht
- Zufällige Einheitenauswahl
- Einfache Angriffe und Bewegungen

### Mittel
- Priorisiert Einheiten mit hoher HP
- Verwendet Spezialfähigkeiten bei Bedarf
- Berücksichtigt Terrain-Effekte

### Schwer
- Komplexe Positionierungsstrategien
- Bewertet Bedrohungen und Chancen
- Nutzt Einheitenpaarungen optimal
- Strategische Nutzung von Terrain

## Technische Details

- **Spielbrett**: 9x9 Felder
- **Grafik**: Pygame-basierte GUI mit Einheitenbildern
- **Animationen**: Angriffs- und Bewegungsanimationen
- **KI**: Drei Schwierigkeitsgrade mit verschiedenen Strategien
- **Terrain**: Vier verschiedene Terrain-Typen mit unterschiedlichen Effekten
