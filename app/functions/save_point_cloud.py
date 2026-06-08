import os
import numpy as np
import open3d as o3d
import numpy as np

def save_point_cloud(depth, points, save_path,model):

    if points is None:
        return

    xs = points[:, 0].astype(np.float32)
    ys = points[:, 1].astype(np.float32)

    z = depth[ys.astype(np.int32), xs.astype(np.int32)].astype(np.float32)

    h, w = depth.shape

    # centrar nube
    X = xs - (w / 2)
    Y = -(ys - (h / 2))

    # escala visual
    Z = z * 2.0

    points_3d = np.stack((X, Y, Z), axis=1)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points_3d)

    os.makedirs(save_path, exist_ok=True)

    ply_path = os.path.join(
        save_path,
        "cloud_points_visual.ply"
    )

    o3d.io.write_point_cloud(
        ply_path,
        pcd,
        write_ascii=False,
        compressed=True
    )

    print(f"PLY guardado en: {ply_path}")


def export_point_cloud_relative(depth_map, color_image, output_ply_path, mask_points=None, step=4, depth_visual = 20.0):
    h, w = depth_map.shape
    print(depth_visual)

    if mask_points is not None:

        xs = mask_points[:, 0]
        ys = mask_points[:, 1]

        xs = xs[::step]
        ys = ys[::step]

        z = depth_map[ys, xs].astype(np.float32)
        z_centered = z - np.median(z)

        exaggeration = depth_visual

        Z = z_centered * exaggeration

        X = xs.astype(np.float32) - (w / 2)
        Y = -(ys.astype(np.float32) - (h / 2))

        points_3d = np.stack((X, Y, Z), axis=1)

        colors = color_image[ys, xs]

    else:

        if step > 1:
            depth_map = depth_map[::step, ::step]
            color_image = color_image[::step, ::step]

        h2, w2 = depth_map.shape

        u = np.arange(w2)
        v = np.arange(h2)

        uu, vv = np.meshgrid(u, v)

        z = depth_map.astype(np.float32)
        z_centered = z - np.median(z)

        exaggeration = depth_visual

        Z = z_centered * exaggeration

        X = (uu * step).astype(np.float32) - (w / 2)
        Y = -((vv * step).astype(np.float32) - (h / 2))

        points_3d = np.stack(
            (X, Y, Z),
            axis=-1
        ).reshape(-1, 3)

        colors = color_image.reshape(-1, 3)

    colors = colors[:, ::-1]

    valid_mask = ~np.isnan(points_3d).any(axis=1)

    points_3d = points_3d[valid_mask]
    colors = colors[valid_mask]

    num_points = len(points_3d)

    print(f"Puntos válidos: {num_points}")

    with open(output_ply_path, 'wb') as f:

        header = (
            f"ply\n"
            f"format binary_little_endian 1.0\n"
            f"element vertex {num_points}\n"
            f"property float x\n"
            f"property float y\n"
            f"property float z\n"
            f"property uchar red\n"
            f"property uchar green\n"
            f"property uchar blue\n"
            f"end_header\n"
        )

        f.write(header.encode('ascii'))

        vertex_data = np.empty(
            num_points,
            dtype=[
                ('x', 'f4'),
                ('y', 'f4'),
                ('z', 'f4'),
                ('r', 'u1'),
                ('g', 'u1'),
                ('b', 'u1')
            ]
        )

        vertex_data['x'] = points_3d[:, 0]
        vertex_data['y'] = points_3d[:, 1]
        vertex_data['z'] = points_3d[:, 2]

        vertex_data['r'] = colors[:, 0]
        vertex_data['g'] = colors[:, 1]
        vertex_data['b'] = colors[:, 2]

        f.write(vertex_data.tobytes())

        # remove return if only we need to save it
        return (
            points_3d.astype(np.float32),
            colors.astype(np.uint8),
        )


def export_point_cloud_meters(depth_map, color_image, output_ply_path, name_model,fx=None, fy=None, cx=None, cy=None, mask_points=None,step=4, depth_visual = 20.0):

    print(f"Generando nube {name_model}...")

    h, w = depth_map.shape

    if fx is None:
        fx = w * 1.2

    if fy is None:
        fy = fx

    if cx is None:
        cx = w / 2

    if cy is None:
        cy = h / 2

    if mask_points is not None:

        xs = mask_points[:, 0][::step]
        ys = mask_points[:, 1][::step]

        Z = depth_map[
            ys.astype(np.int32),
            xs.astype(np.int32)
        ].astype(np.float32)

        X = ((xs - cx) * Z) / fx
        Y = -((ys - cy) * Z) / fy

        points_3d = np.stack(
            (X, Y, Z),
            axis=1
        )

        colors = color_image[
            ys.astype(np.int32),
            xs.astype(np.int32)
        ]

    else:

        if step > 1:
            depth_map = depth_map[::step, ::step]
            color_image = color_image[::step, ::step]

        h2, w2 = depth_map.shape

        u = np.arange(w2)
        v = np.arange(h2)

        uu, vv = np.meshgrid(u, v)

        uu = uu * step
        vv = vv * step

        Z = depth_map.astype(np.float32)

        X = ((uu - cx) * Z) / fx
        Y = -((vv - cy) * Z) / fy

        points_3d = np.stack(
            (X, Y, Z),
            axis=-1
        ).reshape(-1, 3)

        colors = color_image.reshape(-1, 3)

    colors = colors[:, ::-1]

    valid_mask = (
        ~np.isnan(points_3d).any(axis=1)
    ) & (
        points_3d[:, 2] > 0
    )

    points_3d = points_3d[valid_mask]
    colors = colors[valid_mask]

    points_3d *= 3000.0
    center = np.median(points_3d, axis=0)
    points_3d -= center

    colors = colors[valid_mask]

    num_points = len(points_3d)

    print(f"Puntos válidos: {num_points}")

    with open(output_ply_path, 'wb') as f:

        header = (
            f"ply\n"
            f"format binary_little_endian 1.0\n"
            f"element vertex {num_points}\n"
            f"property float x\n"
            f"property float y\n"
            f"property float z\n"
            f"property uchar red\n"
            f"property uchar green\n"
            f"property uchar blue\n"
            f"end_header\n"
        )

        f.write(header.encode('ascii'))

        vertex_data = np.empty(
            num_points,
            dtype=[
                ('x', 'f4'),
                ('y', 'f4'),
                ('z', 'f4'),
                ('r', 'u1'),
                ('g', 'u1'),
                ('b', 'u1')
            ]
        )

        vertex_data['x'] = points_3d[:, 0]
        vertex_data['y'] = points_3d[:, 1]
        vertex_data['z'] = points_3d[:, 2]

        vertex_data['r'] = colors[:, 0]
        vertex_data['g'] = colors[:, 1]
        vertex_data['b'] = colors[:, 2]

        f.write(vertex_data.tobytes())
        return (
                points_3d.astype(np.float32),
                colors.astype(np.uint8),
        )
