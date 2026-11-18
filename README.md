# caddy_ai2_ros2_sensors_gps_ublox

GPS **u-blox NEO-M8P-2** (USB `1546:01a8`; el driver lo identifica con firmware `HPG 1.40 REF`, protocolo 20.30) adicional de la ZED Box del **Caddy AI2**.
Es solo configuración, regla udev, lanzador y fragmento de descripción sobre el driver
[`ublox_gps`](https://index.ros.org/p/ublox_gps/) (KumarRobotics, paquete `apt` de Jazzy): no hay fork ni código propio.

**ROS 2:** Jazzy | **Equipo:** ZED Box (Jetson Orin NX) | **Proyecto:** CERVAREC | Licencia CC BY 4.0

## Estado

| Qué | Estado |
|---|---|
| Receptor reconocido en la ZED Box, emite NMEA | ✅ (16-nov-2026) |
| Paquete (config, udev, launch, URDF) | ✅ probado en la ZED Box (18-nov-2026): el nodo configura el receptor y publica `ublox/fix` a **5,00 Hz** |
| Regla udev `/dev/ublox` | ✅ |
| Fix | ⏳ sin cielo no hay satélites (0 en GPS/GLONASS/Galileo); probar a cielo abierto |

**Papel:** receptor **secundario**. La fuente de posición principal es el GPS del **SBG IG-500N** (LattePanda); este u-blox queda para
comparar y como redundancia, y **no entra en el EKF por defecto**. Si más adelante se fusiona, se decide al probarlo en el vehículo
(`navsat_transform_node` admite un solo `NavSatFix` de entrada, así que habría que elegir uno o promediarlos antes).
Tampoco es el GNSS integrado de la ZED Box (`1546:01a9`), que usa el wrapper de la ZED: **no abrir ese puerto**.

## Instalar (una vez, en la ZED Box)

```bash
sudo apt install ros-jazzy-ublox-gps
sudo cp udev/99-ublox.rules /etc/udev/rules.d/ && sudo udevadm control --reload && sudo udevadm trigger
ls -l /dev/ublox          # -> ttyACMx (el número cambia, el symlink no)
```

La regla identifica por `idProduct` porque los `ttyACMx` cambian de número según el orden de arranque.

## Lanzar

```bash
ros2 launch caddy_ai2_ros2_sensors_gps_ublox ublox.launch.py            # port:=/dev/ublox frame_id:=gps_ublox_link
ros2 topic echo /ublox/fix --once       # status.status: -1 sin fix, 0 fix, 2 con corrección
ros2 topic echo /ublox/navpvt --once    # num_sv y fix_type: satélites usados, útil mientras no hay fix
```

Topics (remapeados al patrón del resto del robot, `<sensor>/...`): `ublox/fix` (`NavSatFix`), `ublox/fix_velocity`,
`ublox/navpvt`, `ublox/navstatus`, `ublox/monhw`. No se publica información por satélite (el M8P no la da con este driver).

**Firmware HPG REF:** es la variante de estación base RTK, así que el driver exige `tmode3` (aquí `0`: base desactivada, receptor normal) y avisa de que `nav_rate` debe ser 1. Como rover RTK haría falta el firmware HPG *Rover*, no es el caso.

**Primer arranque:** el nodo reconfigura los GNSS (apaga QZSS) y reinicia el receptor en frío, tarda ~15 s. Los siguientes arranques ya no lo hacen. Los parámetros numéricos como `rate` deben ser `double` (`5.0`).

Config en `config/ublox_m8.yaml`: 5 Hz, modelo dinámico `automotive`, GPS + GLONASS, **sin guardar nada en la memoria del receptor**.

## Comprobar sin cielo

Con la antena dentro, `ublox/fix` sale con `status.status = -1` y `navpvt` con `num_sv: 0`: es lo esperado.
Para validar el paquete basta ver el topic publicando; el fix real exige antena a cielo abierto unos minutos.
Alternativa de diagnóstico sin ROS: `timeout 5 cat /dev/ublox` y mirar la sentencia `GGA` (calidad ≥ 1, satélites > 0).

## Pendiente

- Sacar la antena a cielo abierto y confirmar fix y tasa real.
- Medir la pose de la antena en el vehículo y añadir `gps_ublox` a `robot_params.yaml` (el fragmento `description/sensor.urdf.j2` está listo).
- Decidir si este receptor se usa solo para comparar con el SBG o también para redundancia en el EKF.
- Arranque automático (systemd), junto con el resto de sensores de la Jetson.
