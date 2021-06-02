from con_control.models import District
from con_brocast.models import BlackRecord
from whiteList.models import WhiteList

dis_obj = District.objects.all()


def c_whitelist():
    wh_obj = WhiteList.objects.all()
    for wh in wh_obj:
        if wh.Region == "通用":
            wh.district = 1
        else:
            dis = dis_obj.filter(Name=wh.Region)[0]
            wh.district = dis.id
            wh.save()


def c_broadcasting():
    bro_obj = BlackRecord.objects.all()
    for bro in bro_obj:
        if bro.region != 82:
            continue
        locationname = bro.LocationName
        if locationname == "错误":
            bro.region = 82
            continue
        else:
            try:
                region = locationname.split("]")[1]
            except Exception as e:
                bro.region = 82
                bro.save()
                continue
        try:
            dis = dis_obj.filter(Name=region)[0]
        except IndexError:
            bro.region = 82
            bro.save()
            continue
        except Exception as e:
            bro.region = 82
            bro.save()
            continue
        bro.region = dis.id
        bro.save()
