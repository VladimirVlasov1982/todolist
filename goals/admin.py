from django.contrib import admin

from goals.models import GoalCategory, Goal, GoalComment


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated',)
    search_fields = ('title', 'user',)
    readonly_fields = ('created', 'updated',)


class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created', 'updated',)
    search_fields = ('title', 'category',)
    readonly_fields = ('created', 'updated',)


class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'goal', 'created', 'updated',)
    search_fields = ('text',)
    readonly_fields = ('created', 'updated',)


admin.site.register(GoalCategory, GoalCategoryAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(GoalComment, GoalCommentAdmin)
