import os
import sys
import django
proj_path='/var/www/commercialoperator'
sys.path.append(proj_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "commercialoperator.settings")
django.setup()


from commercialoperator.components.proposals.models import Proposal

p=Proposal.objects.last()

print(p.__dict__)

