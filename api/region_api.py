from flask.views import MethodView
from decorators import role_required, jwt_required_with_redis
from models.region import Region, Crop, Precinct, Device
from models.pagebean import PageBean
from models.result import Result
from models.role import Role
from utils import get_current_user


class RegionApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.USER, Role.MANAGER])
    def get(self):
        regions: [Region] = Region.query.order_by(Region.region_id).all()

        data = [region.serialize() for region in regions]

        return Result.success(data=data)


class CropApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.USER, Role.MANAGER])
    def get(self):
        crops: [Crop] = Crop.query.order_by(Crop.crop_id).all()

        data = [crop.serialize() for crop in crops]

        return Result.success(data=data)


class FieldApi(MethodView):
    def get(self):
        pass


class PrecinctApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.MANAGER])
    def get(self):
        user = get_current_user()
        precinct = Precinct.query.filter_by(user_id=user.user_id).first()

        if not precinct:
            return Result.error('当前用户并没有管理区域')

        region_id = precinct.region_id
        precincts = Precinct.query.filter_by(region_id=region_id).all()

        data = [precinct.serialize() for precinct in precincts]

        return Result.success(data=data)


class DeviceApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.MANAGER])
    def get(self):
        user = get_current_user()
        precinct = Precinct.query.filter_by(user_id=user.user_id).first()

        if not precinct:
            return Result.error('当前用户并没有管理区域')

        region_id = precinct.region_id
        devices = Device.query.filter_by(region_id=region_id).all()

        data = [device.serialize() for device in devices]

        return Result.success(data=PageBean.data(data=data, count=len(data)))
