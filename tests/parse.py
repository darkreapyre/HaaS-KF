import argparse
import warnings
import sys

def create_generators(args):
    print(args)

def check_args(parsed_args):
    """
    Function to check for inherent contradictions within parsed arguments.
    For example, batch_size < num_gpus
    Intended to raise errors prior to backend initialisation.

    :param parsed_args: parser.parse_args()
    :return: parsed_args
    """
    if parsed_args.dataset_type == 'coco':
        parsed_args.coco_path = parsed_args.dataset_path

    if parsed_args.dataset_type =='pascal':
        parsed_args.pascal_path = parsed_args.dataset_path

    if parsed_args.dataset_type == 'kitti':
        parsed_args.kitti_path = parsed_args.dataset_path

    if parsed_args.multi_gpu > 1 and parsed_args.batch_size < parsed_args.multi_gpu:
        raise ValueError(
            "Batch size ({}) must be equal to or higher than the number of GPUs ({})".format(parsed_args.batch_size,
                                                                                             parsed_args.multi_gpu))

    if parsed_args.multi_gpu > 1 and parsed_args.snapshot:
        raise ValueError(
            "Multi GPU training ({}) and resuming from snapshots ({}) is not supported.".format(parsed_args.multi_gpu,
                                                                                                parsed_args.snapshot))

    if parsed_args.multi_gpu > 1 and not parsed_args.multi_gpu_force:
        raise ValueError("Multi-GPU support is experimental, use at own risk! Run with --multi-gpu-force if you wish to continue.")

    if 'resnet' not in parsed_args.backbone:
        warnings.warn('Using experimental backbone {}. Only resnet50 has been properly tested.'.format(parsed_args.backbone))

    return parsed_args

def parse_args(args):
    parser = argparse.ArgumentParser(description='Simple training script for training a RetinaNet network.')
#    subparsers = parser.add_subparsers(help='Arguments for specific dataset types.', dest='dataset_type')
#    subparsers.required = True

#    coco_parser = subparsers.add_parser('coco')
#    coco_parser.add_argument('coco_path', help='Path to dataset directory (ie. /tmp/COCO).')

#    pascal_parser = subparsers.add_parser('pascal')
#    pascal_parser.add_argument('pascal_path', help='Path to dataset directory (ie. /tmp/VOCdevkit).')

#    kitti_parser = subparsers.add_parser('kitti')
#    kitti_parser.add_argument('kitti_path', help='Path to dataset directory (ie. /tmp/kitti).')

#    def csv_list(string):
#        return string.split(',')

#    oid_parser = subparsers.add_parser('oid')
#    oid_parser.add_argument('main_dir', help='Path to dataset directory.')
#    oid_parser.add_argument('--version',  help='The current dataset version is v4.', default='v4')
#    oid_parser.add_argument('--labels-filter',  help='A list of labels to filter.', type=csv_list, default=None)
#    oid_parser.add_argument('--annotation-cache-dir', help='Path to store annotation cache.', default='.')
#    oid_parser.add_argument('--fixed-labels', help='Use the exact specified labels.', default=False)

#    csv_parser = subparsers.add_parser('csv')
#    csv_parser.add_argument('annotations', help='Path to CSV file containing annotations for training.')
#    csv_parser.add_argument('classes', help='Path to a CSV file containing class label mapping.')
#    csv_parser.add_argument('--val-annotations', help='Path to CSV file containing annotations for validation (optional).')

    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--snapshot',          help='Resume training from a snapshot.')
    group.add_argument('--imagenet-weights',  help='Initialize the model with pretrained imagenet weights. This is the default behaviour.', action='store_const', const=True, default=True)
    group.add_argument('--weights',           help='Initialize the model with weights from a file.')
    group.add_argument('--no-weights',        help='Don\'t initialize the model with any weights.', dest='imagenet_weights', action='store_const', const=False)

    parser.add_argument('--dataset',         help='Training dataset Name.', dest='dataset_type')
    
    parser.add_argument('--dataset-path',    help='Path to the training dataset.', dest='dataset_path', type=str)
    
    parser.add_argument('--backbone',        help='Backbone model used by retinanet.', default='resnet50', type=str)
    parser.add_argument('--batch-size',      help='Size of the batches.', default=1, type=int)
    parser.add_argument('--gpu',             help='Id of the GPU to use (as reported by nvidia-smi).')
    parser.add_argument('--multi-gpu',       help='Number of GPUs to use for parallel processing.', type=int, default=0)
    parser.add_argument('--multi-gpu-force', help='Extra flag needed to enable (experimental) multi-gpu support.', action='store_true')
    parser.add_argument('--epochs',          help='Number of epochs to train.', type=int, default=50)
    parser.add_argument('--steps',           help='Number of steps per epoch.', type=int, default=10000)
    parser.add_argument('--snapshot-path',   help='Path to store snapshots of models during training (defaults to \'./snapshots\')', default='./snapshots')
    parser.add_argument('--tensorboard-dir', help='Log directory for Tensorboard output', default='./logs')
    parser.add_argument('--no-snapshots',    help='Disable saving snapshots.', dest='snapshots', action='store_false')
    parser.add_argument('--no-evaluation',   help='Disable per epoch evaluation.', dest='evaluation', action='store_false')
    parser.add_argument('--freeze-backbone', help='Freeze training of backbone layers.', action='store_true')
    parser.add_argument('--random-transform', help='Randomly transform image and annotations.', action='store_true')
    parser.add_argument('--image-min-side', help='Rescale the image so the smallest side is min_side.', type=int, default=800)
    parser.add_argument('--image-max-side', help='Rescale the image if the largest side is larger than max_side.', type=int, default=1333)

    return check_args(parser.parse_args(args))


def main(args=None):
    # parse arguments
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)
    create_generators(args)

if __name__ == '__main__':
    main()