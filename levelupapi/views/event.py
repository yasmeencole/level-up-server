"""View module for handling requests about game types"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from levelupapi.models import Game, Event, Gamer, AttendingGamer
from levelupapi.views.game import GameSerializer


class EventView(ViewSet):
    @action(methods=['post', 'delete'], detail=True)
    def signup(self, request, pk=None):
        """Managing gamers signing up for events"""
        # Django uses the `Authorization` header to determine
        # which user is making the request to sign up
        gamer = Gamer.objects.get(user=request.auth.user)
        
        try:
            # Handle the case if the client specifies a game
            # that doesn't exist
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response(
                {'message': 'Event does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # A gamer wants to sign up for an event
        if request.method == "POST":
            try:
                # Using the attending_gamer field on the event makes it simple to add a gamer to the event
                # .add(gamer) will insert into the join table a new row the gamer_id and the event_id
                event.attending_gamer.add(gamer)
                return Response({}, status=status.HTTP_201_CREATED)
            except Exception as ex:
                return Response({'message': ex.args[0]})

        # User wants to leave a previously joined event
        elif request.method == "DELETE":
            try:
                # The many to many relationship has a .remove method that removes the gamer from the attending_gamer list
                # The method deletes the row in the join table that has the gamer_id and event_id
                event.attending_gamer.remove(gamer)
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response({'message': ex.args[0]})

    """Level up events"""

    def create(self, request):
        """Handle POST operations for events

        Returns:
            Response -- JSON serialized event instance
        """
        gamer = Gamer.objects.get(user=request.auth.user)

        event = Event()
        event.time = request.data["time"]
        event.date = request.data["date"]
        event.name = request.data["name"]
        event.description = request.data["description"]
        event.host = gamer

        game = Game.objects.get(pk=request.data["game_id"])
        event.game = game

        try:
            event.save()
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single event

        Returns:
            Response -- JSON serialized game instance
        """
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data)
        except Exception:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for an event

        Returns:
            Response -- Empty body with 204 status code
        """
        host = Gamer.objects.get(user=request.auth.user)

        event = Event.objects.get(pk=pk)
        event.name = request.data["name"]
        event.description = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]
        event.host = host

        game = Game.objects.get(pk=request.data["gameId"])
        event.game = game
        event.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single game

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            event = Event.objects.get(pk=pk)
            event.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to events resource

        Returns:
            Response -- JSON serialized list of events
        """
        # Get the current authenticated user
        gamer = Gamer.objects.get(user=request.auth.user)
        events = Event.objects.all()
        
        # Set the `joined` property on every event
        for event in events:
            event.joined = None

            # Check to see if the gamer is in the attending_gamer list on the event
            event.joined = gamer in event.attending_gamer.all()

        # Support filtering events by game
        game = self.request.query_params.get('gameId', None)
        if game is not None:
            events = events.filter(game__id=game)

        serializer = EventSerializer(
            events, many=True, context={'request': request})
        return Response(serializer.data)

class EventUserSerializer(serializers.ModelSerializer):
    """JSON serializer for event host's related Django user"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class EventGamerSerializer(serializers.ModelSerializer):
    """JSON serializer for event host"""
    user = EventUserSerializer(many=False)

    class Meta:
        model = Gamer
        fields = ['user']

class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events"""
    host = EventGamerSerializer(many=False)
    game = GameSerializer(many=False)

    class Meta:
        model = Event
        fields = ('id', 'host', 'game', 'name', 'description', 'attending_gamer','date', 'time', 'joined')

class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for games"""
    class Meta:
        model = Game
        fields = ('id', 'game_type"','title', 'maker', 'number_of_players', 'skill_level')