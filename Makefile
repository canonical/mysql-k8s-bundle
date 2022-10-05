BUILD_DIRECTORY := ./build_directory

clean:
	rm -rf $(BUILD_DIRECTORY)

build: clean
	mkdir -p $(BUILD_DIRECTORY)
	cp ./releases/latest/mysql-k8s-bundle.yaml $(BUILD_DIRECTORY)/bundle.yaml
	cp ./charmcraft.yaml $(BUILD_DIRECTORY)
	cp ./metadata.yaml $(BUILD_DIRECTORY)
	cp ./README.md $(BUILD_DIRECTORY)
	charmcraft pack --destructive-mode --project-dir $(BUILD_DIRECTORY)

deploy: build
	juju deploy $(BUILD_DIRECTORY)/mysql-k8s-bundle.zip --trust

destroy-model:
	juju destroy-model --force --destroy-storage $(shell juju models --format=yaml | yq ".current-model")

release:
	charmcraft upload $(BUILD_DIRECTORY)/*.zip
	charmcraft release mysql-k8s-bundle --revision $(shell charmcraft revisions mysql-k8s-bundle | awk 'NR==2 {print $$1}') --channel=latest/edge
