# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Organization'
        db.create_table('freeform_data_organization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization_size', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('organization_name', self.gf('django.db.models.fields.TextField')(default='')),
            ('premium_service_subscriptions', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('freeform_data', ['Organization'])

        # Adding model 'UserProfile'
        db.create_table('freeform_data_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True, null=True, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freeform_data.Organization'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('freeform_data', ['UserProfile'])

        # Adding model 'Course'
        db.create_table('freeform_data_course', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freeform_data.Organization'])),
            ('course_name', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('freeform_data', ['Course'])

        # Adding M2M table for field users on 'Course'
        db.create_table('freeform_data_course_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['freeform_data.course'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('freeform_data_course_users', ['course_id', 'user_id'])

        # Adding model 'Problem'
        db.create_table('freeform_data_problem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('max_target_scores', self.gf('django.db.models.fields.TextField')(default='[1]')),
            ('number_of_additional_predictors', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('prompt', self.gf('django.db.models.fields.TextField')(default='')),
            ('premium_feedback_models', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('name', self.gf('django.db.models.fields.TextField')(default='')),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('freeform_data', ['Problem'])

        # Adding M2M table for field courses on 'Problem'
        db.create_table('freeform_data_problem_courses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('problem', models.ForeignKey(orm['freeform_data.problem'], null=False)),
            ('course', models.ForeignKey(orm['freeform_data.course'], null=False))
        ))
        db.create_unique('freeform_data_problem_courses', ['problem_id', 'course_id'])

        # Adding model 'Essay'
        db.create_table('freeform_data_essay', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('problem', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freeform_data.Problem'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('essay_text', self.gf('django.db.models.fields.TextField')()),
            ('additional_predictors', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('essay_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('has_been_ml_graded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('freeform_data', ['Essay'])

        # Adding model 'EssayGrade'
        db.create_table('freeform_data_essaygrade', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('essay', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freeform_data.Essay'])),
            ('target_scores', self.gf('django.db.models.fields.TextField')()),
            ('grader_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('feedback', self.gf('django.db.models.fields.TextField')()),
            ('annotated_text', self.gf('django.db.models.fields.TextField')(default='')),
            ('premium_feedback_scores', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('success', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('confidence', self.gf('django.db.models.fields.DecimalField')(default=1, max_digits=10, decimal_places=9)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('freeform_data', ['EssayGrade'])

        # Adding model 'StudentGroup'
        db.create_table('freeform_data_studentgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freeform_data.UserProfile'])),
        ))
        db.send_create_signal('freeform_data', ['StudentGroup'])

        # Adding model 'TeacherGroup'
        db.create_table('freeform_data_teachergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freeform_data.UserProfile'])),
        ))
        db.send_create_signal('freeform_data', ['TeacherGroup'])

        # Adding model 'AdministratorGroup'
        db.create_table('freeform_data_administratorgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freeform_data.UserProfile'])),
        ))
        db.send_create_signal('freeform_data', ['AdministratorGroup'])

        # Adding model 'GraderGroup'
        db.create_table('freeform_data_gradergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['freeform_data.UserProfile'])),
        ))
        db.send_create_signal('freeform_data', ['GraderGroup'])


    def backwards(self, orm):
        # Deleting model 'Organization'
        db.delete_table('freeform_data_organization')

        # Deleting model 'UserProfile'
        db.delete_table('freeform_data_userprofile')

        # Deleting model 'Course'
        db.delete_table('freeform_data_course')

        # Removing M2M table for field users on 'Course'
        db.delete_table('freeform_data_course_users')

        # Deleting model 'Problem'
        db.delete_table('freeform_data_problem')

        # Removing M2M table for field courses on 'Problem'
        db.delete_table('freeform_data_problem_courses')

        # Deleting model 'Essay'
        db.delete_table('freeform_data_essay')

        # Deleting model 'EssayGrade'
        db.delete_table('freeform_data_essaygrade')

        # Deleting model 'StudentGroup'
        db.delete_table('freeform_data_studentgroup')

        # Deleting model 'TeacherGroup'
        db.delete_table('freeform_data_teachergroup')

        # Deleting model 'AdministratorGroup'
        db.delete_table('freeform_data_administratorgroup')

        # Deleting model 'GraderGroup'
        db.delete_table('freeform_data_gradergroup')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'freeform_data.administratorgroup': {
            'Meta': {'object_name': 'AdministratorGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freeform_data.UserProfile']"})
        },
        'freeform_data.course': {
            'Meta': {'object_name': 'Course'},
            'course_name': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freeform_data.Organization']"}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'freeform_data.essay': {
            'Meta': {'object_name': 'Essay'},
            'additional_predictors': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'essay_text': ('django.db.models.fields.TextField', [], {}),
            'essay_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'has_been_ml_graded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'problem': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freeform_data.Problem']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'freeform_data.essaygrade': {
            'Meta': {'object_name': 'EssayGrade'},
            'annotated_text': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'confidence': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '10', 'decimal_places': '9'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'essay': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freeform_data.Essay']"}),
            'feedback': ('django.db.models.fields.TextField', [], {}),
            'grader_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'premium_feedback_scores': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'target_scores': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'freeform_data.gradergroup': {
            'Meta': {'object_name': 'GraderGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freeform_data.UserProfile']"})
        },
        'freeform_data.organization': {
            'Meta': {'object_name': 'Organization'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'organization_name': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'organization_size': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'premium_service_subscriptions': ('django.db.models.fields.TextField', [], {'default': "'[]'"})
        },
        'freeform_data.problem': {
            'Meta': {'object_name': 'Problem'},
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['freeform_data.Course']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_target_scores': ('django.db.models.fields.TextField', [], {'default': "'[1]'"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'number_of_additional_predictors': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'premium_feedback_models': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'prompt': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        'freeform_data.studentgroup': {
            'Meta': {'object_name': 'StudentGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freeform_data.UserProfile']"})
        },
        'freeform_data.teachergroup': {
            'Meta': {'object_name': 'TeacherGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freeform_data.UserProfile']"})
        },
        'freeform_data.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['freeform_data.Organization']", 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['freeform_data']