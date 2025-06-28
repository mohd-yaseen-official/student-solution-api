from rest_framework import serializers

from homeworks.models import Homework
from timetable.models import Subject


class HomeworkSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    subject = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Homework
        fields = [
            'id',
            'title',
            'subject_name',
            'subject',
            'is_completed',
            'is_deleted',
            'created_at',
            'due_date'
        ]

    def create(self, validated_data):
        subject_name = validated_data.pop('subject_name', '').strip().lower()

        if subject_name:
            subject, _ = Subject.objects.get_or_create(
                name__iexact=subject_name,
                defaults={'name': subject_name.capitalize()}
            )
        else:
            subject = None

        validated_data['subject'] = subject
        validated_data['user'] = self.context['request'].user
        return Homework.objects.create(**validated_data)
