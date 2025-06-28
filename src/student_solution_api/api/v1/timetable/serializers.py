# serializers.py
from rest_framework import serializers
from timetable.models import Timetable, Day, Period, Subject

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ['order', 'subject']

class DaySerializer(serializers.ModelSerializer):
    periods = PeriodSerializer(many=True)
    id = serializers.IntegerField(source='pk', read_only=True)
    name = serializers.CharField(source='get_name_display', read_only=True)
    
    class Meta:
        model = Day
        fields = ['id', 'name', 'periods']

class TimetableCreateSerializer(serializers.ModelSerializer):
    days = serializers.ListField(write_only=True)
    
    class Meta:
        model = Timetable
        fields = ['name', 'days']
    
    def create(self, validated_data):
        days_data = validated_data.pop('days')
        user = self.context['request'].user
        timetable = Timetable.objects.create(user=user, **validated_data)
        
        for day_data in days_data:
            day_id = day_data['id']
            periods_data = day_data['periods']
            
            # Get the day using the provided ID
            try:
                day = Day.objects.get(pk=day_id)
            except Day.DoesNotExist:
                raise serializers.ValidationError(f"Day with id {day_id} does not exist")
            
            for period_data in periods_data:
                subject_name = period_data['subject'].strip()
                subject, _ = Subject.objects.get_or_create(
                    name__iexact=subject_name,
                    defaults={'name': subject_name.title()}
                )
                
                Period.objects.create(
                    timetable=timetable,
                    day=day,
                    order=period_data['order'],
                    subject=subject
                )
        
        return timetable

class TimetableManageSerializer(serializers.ModelSerializer):
    days = serializers.ListField(write_only=True, required=False)
    
    class Meta:
        model = Timetable
        fields = ['id', 'name', 'days']
    
    def to_representation(self, instance):
        # This is your old get_days logic
        days_dict = {}
        periods = instance.periods.select_related('day', 'subject').all()
        for period in periods:
            day_id = period.day.pk
            if day_id not in days_dict:
                days_dict[day_id] = {
                    'id': day_id,
                    'name': period.day.get_name_display(),
                    'periods': []
                }
            days_dict[day_id]['periods'].append({
                'order': period.order,
                'subject': period.subject.name
            })
        for day_data in days_dict.values():
            day_data['periods'].sort(key=lambda x: x['order'])
        data = super().to_representation(instance)
        data['days'] = sorted(days_dict.values(), key=lambda x: x['id'])
        return data
    
    def update(self, instance, validated_data):
        days_data = validated_data.pop('days', None)
        
        # Update timetable name
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        
        # Only update periods if days data is provided
        if days_data is not None:
            for day_data in days_data:
                day_id = day_data['id']
                periods_data = day_data.get('periods', [])
                try:
                    day = Day.objects.get(pk=day_id)
                except Day.DoesNotExist:
                    raise serializers.ValidationError(f"Day with id {day_id} does not exist")
                
                for period_data in periods_data:
                    subject_name = period_data['subject'].strip()
                    subject, _ = Subject.objects.get_or_create(
                        name__iexact=subject_name,
                        defaults={'name': subject_name.title()}
                    )
                    Period.objects.update_or_create(
                        timetable=instance,
                        day=day,
                        order=period_data['order'],
                        defaults={'subject': subject}
                    )
        
        return instance