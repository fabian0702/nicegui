from dataclasses import dataclass
from typing import Any, Callable, Optional

from typing_extensions import Self

from .. import binding
from ..awaitable_response import AwaitableResponse, NullResponse
from ..dataclasses import KWONLY_SLOTS
from ..element import Element
from ..events import (GenericEventArguments, SceneClickEventArguments, SceneClickHit,
                      handle_event)
from .scene_object3d import Object3D


@dataclass(**KWONLY_SLOTS)
class SceneCamera:
    x: float = 0
    y: float = -3
    z: float = 5
    look_at_x: float = 0
    look_at_y: float = 0
    look_at_z: float = 0
    up_x: float = 0
    up_y: float = 0
    up_z: float = 1


class Scene_View(Element,
            component='scene_view.js',
            libraries=['lib/tween/tween.umd.js'],
            exposed_libraries=[
                'lib/three/three.module.js',
                'lib/three/modules/CSS2DRenderer.js',
                'lib/three/modules/CSS3DRenderer.js',
            ]):

    def __init__(self,
                 width: int = 400,
                 height: int = 300,
                 on_click: Optional[Callable[..., Any]] = None,
                 parent_scene:Self=None,
                 ) -> None:
        """3D Scene

        Display a 3D scene using `three.js <https://threejs.org/>`_.
        Currently NiceGUI supports boxes, spheres, cylinders/cones, extrusions, straight lines, curves and textured meshes.
        Objects can be translated, rotated and displayed with different color, opacity or as wireframes.
        They can also be grouped to apply joint movements.

        :param width: width of the canvas
        :param height: height of the canvas
        :param grid: whether to display a grid
        :param on_click: callback to execute when a 3D object is clicked
        :param on_drag_start: callback to execute when a 3D object is dragged
        :param on_drag_end: callback to execute when a 3D object is dropped
        :param drag_constraints: comma-separated JavaScript expression for constraining positions of dragged objects (e.g. ``'x = 0, z = y / 2'``)
        :param parent_scene: specifies the parent scene for rendering the same scene as the parent
        """
        super().__init__()
        self._props['width'] = width
        self._props['height'] = height
        self._props['parent_id'] = parent_scene.id if parent_scene is not None else ''
        self.camera: SceneCamera = SceneCamera()
        self._click_handler = on_click
        self.is_initialized = False
        self.on('init', self._handle_init)
        self.on('click3d', self._handle_click)


    def __getattribute__(self, name: str) -> Any:
        attribute = super().__getattribute__(name)
        if isinstance(attribute, type) and issubclass(attribute, Object3D):
            Object3D.current_scene = self
        return attribute

    def _handle_init(self, e: GenericEventArguments) -> None:
        self.is_initialized = True
        with self.client.individual_target(e.args['socket_id']):
            self.move_camera(duration=0)
            for obj in self.objects.values():
                obj.send()

    def run_method(self, name: str, *args: Any, timeout: float = 1, check_interval: float = 0.01) -> AwaitableResponse:
        if not self.is_initialized:
            return NullResponse()
        return super().run_method(name, *args, timeout=timeout, check_interval=check_interval)

    def _handle_click(self, e: GenericEventArguments) -> None:
        arguments = SceneClickEventArguments(
            sender=self,
            client=self.client,
            click_type=e.args['click_type'],
            button=e.args['button'],
            alt=e.args['alt_key'],
            ctrl=e.args['ctrl_key'],
            meta=e.args['meta_key'],
            shift=e.args['shift_key'],
            hits=[SceneClickHit(
                object_id=hit['object_id'],
                object_name=hit['object_name'],
                x=hit['point']['x'],
                y=hit['point']['y'],
                z=hit['point']['z'],
            ) for hit in e.args['hits']],
        )
        handle_event(self._click_handler, arguments)

    def __len__(self) -> int:
        return len(self.objects)

    def move_camera(self,
                    x: Optional[float] = None,
                    y: Optional[float] = None,
                    z: Optional[float] = None,
                    look_at_x: Optional[float] = None,
                    look_at_y: Optional[float] = None,
                    look_at_z: Optional[float] = None,
                    up_x: Optional[float] = None,
                    up_y: Optional[float] = None,
                    up_z: Optional[float] = None,
                    duration: float = 0.5) -> None:
        """Move the camera to a new position.

        :param x: camera x position
        :param y: camera y position
        :param z: camera z position
        :param look_at_x: camera look-at x position
        :param look_at_y: camera look-at y position
        :param look_at_z: camera look-at z position
        :param up_x: x component of the camera up vector
        :param up_y: y component of the camera up vector
        :param up_z: z component of the camera up vector
        :param duration: duration of the movement in seconds (default: `0.5`)
        """
        self.camera.x = self.camera.x if x is None else x
        self.camera.y = self.camera.y if y is None else y
        self.camera.z = self.camera.z if z is None else z
        self.camera.look_at_x = self.camera.look_at_x if look_at_x is None else look_at_x
        self.camera.look_at_y = self.camera.look_at_y if look_at_y is None else look_at_y
        self.camera.look_at_z = self.camera.look_at_z if look_at_z is None else look_at_z
        self.camera.up_x = self.camera.up_x if up_x is None else up_x
        self.camera.up_y = self.camera.up_y if up_y is None else up_y
        self.camera.up_z = self.camera.up_z if up_z is None else up_z
        self.run_method('move_camera',
                        self.camera.x, self.camera.y, self.camera.z,
                        self.camera.look_at_x, self.camera.look_at_y, self.camera.look_at_z,
                        self.camera.up_x, self.camera.up_y, self.camera.up_z, duration)

    def _handle_delete(self) -> None:
        binding.remove(list(self.objects.values()))
        super()._handle_delete()