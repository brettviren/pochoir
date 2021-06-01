export POCHOIR_STORE=$(pwd)/"${1:-store}"

pochoir plot-image -a store/boundary/weight2d.npz -o plots/weight2d/image_BVA_weight2D.png -s signedlog
pochoir plot-image -a store/initial/weight2d.npz -o plots/weight2d/image_IVA_weight2D.png -s signedlog

pochoir plot-image -a store/potential/weight2d.npz -o plots/weight2d/image_potential_weight2D.png -s signedlog

pochoir plot-scatter3d -a store/initial/drift3d.npz -o plots/drift3d/image_IVA_drift3D.png -g yes
pochoir plot-scatter3d -a store/boundary/drift3d.npz -o plots/drift3d/image_BVA_drift3D.png -g yes

pochoir plot-scatter3d -a store/initial/weight3d.npz -o plots/weight3d/image_IVA_weight3D.png -g yes
pochoir plot-scatter3d -a store/boundary/weight3d.npz -o plots/weight3d/image_BVA_weight3D.png -g yes

pochoir plot-slice3d -a store/initial/drift3d.npz -o plots/drift3d/image_IVA_drift3D_sliceZ_cath.png -d z -i 0
pochoir plot-slice3d -a store/initial/drift3d.npz -o plots/drift3d/image_IVA_drift3D_sliceZ_coll.png -d z -i 100
pochoir plot-slice3d -a store/initial/drift3d.npz -o plots/drift3d/image_IVA_drift3D_sliceZ_max.png -d z -i -1

pochoir plot-slice3d -a store/initial/weight3d.npz -o plots/weight3d/image_IVA_weight3D_sliceZ_cath.png -d z -i 0
pochoir plot-slice3d -a store/initial/weight3d.npz -o plots/weight3d/image_IVA_weight3D_sliceZ_coll.png -d z -i 100
pochoir plot-slice3d -a store/initial/weight3d.npz -o plots/weight3d/image_IVA_weight3D_sliceZ_max.png -d z -i -1

pochoir plot-slice3d -a store/boundary/weight3d.npz -o plots/weight3d/image_IVA_weight3D_sliceZ_cath.png -d z -i 0
pochoir plot-slice3d -a store/boundary/weight3d.npz -o plots/weight3d/image_IVA_weight3D_sliceZ_coll.png -d z -i 100
pochoir plot-slice3d -a store/boundary/weight3d.npz -o plots/weight3d/image_IVA_weight3D_sliceZ_max.png -d z -i -1

pochoir plot-slice3d -a store/velocity/drift3d.npz -o plots/drift3d/image_velocity_drift3D_sliceZ_mid.png -m yes -s signedlog -d y -i -9

pochoir plot-drift3d -t 4 -p store/paths/drift3d.npz -b store/boundary/drift3d.npz -o plots/drift3d/image_paths_drift3d.png



