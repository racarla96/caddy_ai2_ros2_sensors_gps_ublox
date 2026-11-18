# caddy_ai2_ros2_sensors_gps_ublox

GPS **u-blox M8** (`UBX-M8030`, FW 3.01, USB `1546:01a8`) adicional de la ZED Box del **Caddy AI2**.
Es solo configuración, regla udev, lanzador y fragmento de descripción sobre el driver
[`ublox_gps`](https://index.ros.org/p/ublox_gps/) (KumarRobotics, paquete `apt` de Jazzy): no hay fork ni código propio.

**ROS 2:** Jazzy | **Equipo:** ZED Box (Jetson Orin NX) | **Proyecto:** CERVAREC | Licencia CC BY 4.0

## Estado

| Qué | Estado |
|---|---|
| Receptor reconocido en la ZED Box, emite NMEA | ✅ (16-nov-2026) |
| Paquete (config, udev, launch, URDF) | escrito, **sin probar con el nodo** |
| Fix | ⏳ sin cielo no hay satélites (0 en GPS/GLONASS/Galileo); probar a cielo abierto |

Tres fuentes de posición conviven, cada una con su topic: el GPS del SBG IG-500N (LattePanda), este u-blox y el GNSS integrado de la ZED Box
(`1546:01a9`, lo usa el wrapper de la ZED: **no abrir ese puerto**). Cuál entra en el EKF se decide al probarlas en el vehículo.

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
ros2 topic echo /ublox/navsvinfo --once # satélites vistos y su señal, útil mientras no hay fix
```

Topics (remapeados al patrón del resto del robot, `<sensor>/...`): `ublox/fix` (`NavSatFix`), `ublox/fix_velocity`,
`ublox/navpvt`, `ublox/navstatus`, `ublox/navsvinfo`, `ublox/monhw`.

Config en `config/ublox_m8.yaml`: 5 Hz, modelo dinámico `automotive`, GPS + GLONASS, **sin guardar nada en la memoria del receptor**.

## Comprobar sin cielo

Con la antena dentro, `ublox/fix` sale con `status.status = -1` y `navsvinfo` con pocos satélites y señal baja: es lo esperado.
Para validar el paquete basta ver el topic publicando; el fix real exige antena a cielo abierto unos minutos.
Alternativa de diagnóstico sin ROS: `timeout 5 cat /dev/ublox` y mirar la sentencia `GGA` (calidad ≥ 1, satélites > 0).

## Pendiente

- Probar el nodo en la ZED Box: los nombres de parámetros están verificados contra el binario del driver, pero no se ha ejecutado contra el receptor.
- Sacar la antena a cielo abierto y confirmar fix y tasa real.
- Medir la pose de la antena en el vehículo y añadir `gps_ublox` a `robot_params.yaml` (el fragmento `description/sensor.urdf.j2` está listo).
- Decidir qué fuente entra en `navsat_transform_node` / EKF.
- Arranque automático (systemd), junto con el resto de sensores de la Jetson.
