from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from . serializers import RoomSerializer
from base.api import serializers

@api_view(['GET'])
def getRoutes(request):
    routes=[
        'GET /api', #home
        'GET /api/rooms', #gives JSON array of all the rooms in out db
        'GET /api/rooms/:id' #get a particular room
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms=Room.objects.all()
    serializer=RoomSerializer(rooms,many=True) #true if there are many objs to serialize
    return Response(serializer.data)

@api_view(['GET'])
def getRoom(request,pk):
    room=Room.objects.get(id=pk)
    serializer=RoomSerializer(room,many=False) #true if there are many objs to serialize
    return Response(serializer.data)