# all our targets are phony (no files to check).
.PHONY: help init init2 show apply test
SHELL := /bin/bash
$(VERBOSE).SILENT:
.DEFAULT_GOAL := help


tf_volume_modules = $(shell cd `pwd`/.. && pwd) 
tf_workspace = $(shell cd `pwd`/.. && pwd)
org_dir = $(shell cd `pwd`/org/$(org) && pwd)

subid_short = $(shell export subid=$(ARM_SUBSCRIPTION_ID); echo $${subid: -6})

org_location = $(shell echo $(org) |  awk -F/ '{print $$2}')
org_sub_name = $(shell echo $(org) |  awk -F/ '{print $$1}')
org_namespace = $(shell echo $(org) |  awk -F/ '{print $$3}')
org_infra =     $(shell echo $(org) |  awk -F/ '{print $$4}')
org_env = $(shell echo $(org_sub_name) |  awk -F- '{if ($$NF == "NP") print "npd"; else if ($$NF == "PR") print "prd"; else if ($$NF == "Dev") print "dev"  }')
org_storage_account_name = $(shell echo $(org_sub_name))
org_location_short = $(shell echo $(org_location) | awk  '{print substr($$1,1,3)}')

THIS_DIR := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))

export CURRENT_UID
export CURRENT_GID
export MY_IMAGE

CURRENT_UID := $(shell id -u)
CURRENT_GID := $(shell id -g)


DOCKER_COMPOSE_ANSIBLE := \
				  ANSIBLE_FORCE_COLOR=true \
				  docker-compose run --rm --user="$(CURRENT_UID)"

ANSIBLE_BASH := $(DOCKER_COMPOSE2) --entrypoint="/bin/bash" ansible-playbook
ANSIBLE_PLAYBOOK := $(DOCKER_COMPOSE_ANSIBLE) ansible-playbook

.PHONY generate-dc
## connect to aks cluster 
generate-dc: 
	$(ANSIBLE_PLAYBOOK) -i "localhost" ./config/generate_dc_file.yml --extra-vars "org=$(org)" --extra-vars "@/opt/build/manifest.json" -vvvv

