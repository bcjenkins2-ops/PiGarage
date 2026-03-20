# PiGarage Ordering & Assembly Guide

## 1. Prepare Production Files

Compress all files in the `Production/` folder into a `.zip` or `.rar`, **excluding** the position file (`PiGarage-all-pos.xlsx`). The zip should contain only Gerber and drill files.

## 2. Order PCBs with Assembly

1. Go to [JLCPCB](https://cart.jlcpcb.com/quote) and upload your compressed Gerber file.
2. The default settings should be fine. The main ones to confirm:
   - **Layers:** 2
   - **Thickness:** 1.6mm
   - **Surface Finish:** HASL (lead-free)
   - **Copper Weight:** 1oz
3. Scroll down and select **PCB Assembly**.
4. Set **PCBA Qty** to **2** (this is the minimum). Feel free to share the spare with someone else wanting to use a Pi as their head unit!

## 3. Upload BOM and CPL

- **BOM:** Upload `BOM/BOM.xlsx`
- **CPL (Component Placement List):** Upload `Production/PiGarage-all-pos.xlsx`

## 4. Check Component Orientation

In the **Component Placements** preview, you will need to ensure the components are oriented correctly. Line up each component's dot/pin-1 marker with the corresponding dot on the board. Rotate any that don't match.

## 5. Hand-Solder Remaining Parts

Not all components are available through JLCPCB assembly. Purchase the remaining parts from DigiKey (or your preferred distributor) and hand-solder them:

- **J1** — 40-pin Raspberry Pi GPIO header
- **J2** — Molex Mini-Fit Jr 4-pin power connector
- **J3** — PJ-320B 3.5mm audio jack

Refer to `BOM/PiGarage_BOM.txt` for the full parts list with part numbers.

## 6. Install Software

```bash
sudo mkdir -p /opt/pigarage
sudo cp Software/power_latch.py /opt/pigarage/power_latch.py
sudo cp Software/pigarage.service /etc/systemd/system/pigarage.service
sudo systemctl daemon-reload
sudo systemctl enable pigarage
sudo systemctl start pigarage
```

The service monitors ACC (BCM27) and holds the power latch (BCM25) high. When ACC drops for 3 seconds, the Pi shuts down safely and releases the latch.
