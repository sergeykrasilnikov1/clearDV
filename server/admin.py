from django.contrib import admin
from .models import Video, CompanyLogo, Service, Application, Review, SectionContent

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'youtube_url', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'youtube_url')
    list_editable = ('is_active', 'order')
    ordering = ('order', '-created_at')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'youtube_url', 'video_file')
        }),
        ('Настройки отображения', {
            'fields': ('is_active', 'order')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(CompanyLogo)
class CompanyLogoAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order',)
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('is_active', 'order')
    ordering = ('order',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'logo',)
        }),
        ('Настройки отображения', {
            'fields': ('is_active', 'order')
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'area', 'price', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'order', 'price')
    ordering = ('order', 'name')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'photo')
        }),
        ('Параметры услуги', {
            'fields': ('duration', 'area', 'price')
        }),
        ('Настройки отображения', {
            'fields': ('is_active', 'order')
        }),
    )

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'area', 'service', 'created_at')
    list_filter = ('service', 'created_at')
    search_fields = ('name', 'phone', 'question')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Информация о клиенте', {
            'fields': ('name', 'phone', 'area')
        }),
        ('Детали заявки', {
            'fields': ('service', 'question')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'rating', 'is_active', 'created_at')
    list_filter = ('service', 'rating', 'is_active', 'created_at')
    search_fields = ('name', 'text')
    list_editable = ('is_active', 'rating')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'photo', 'text', 'link')
        }),
        ('Детали отзыва', {
            'fields': ('service', 'rating')
        }),
        ('Настройки отображения', {
            'fields': ('is_active',)
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(SectionContent)
class SectionContentAdmin(admin.ModelAdmin):
    list_display = ('get_section_display', 'title', 'is_active', 'updated_at')
    list_filter = ('is_active', 'section')
    search_fields = ('title', 'subtitle', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('section', 'is_active')
        }),
        ('Контент', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('Информация о записи', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
