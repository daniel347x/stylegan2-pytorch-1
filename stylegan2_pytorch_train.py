import fire
from retry.api import retry_call
from tqdm import tqdm
from stylegan2_pytorch import Trainer, NanException
from datetime import datetime

def train_from_folder(
    data = '/hydration/ffhq/pose/trainB',
    results_dir = '/hydration/results',
    models_dir = './models',
    name = 'run_testsg2_001',
    new = False,
    load_from = -1,
    image_size = 256,
    network_capacity = 64,
    transparent = False,
    batch_size = 1,
    gradient_accumulate_every = 1,
    num_train_steps = 150000,
    learning_rate = 2e-4,
    num_workers =  None,
    save_every = 1000,
    generate = False,
    generate_interpolation = False,
    save_frames = False,
    num_image_tiles = 8,
    trunc_psi = 0.75,
    fp16=False,
    cl_reg = False,
    fq_layers = [],
    fq_dict_size = 256,
    attn_layers = [],
    no_const = False,
    aug_prob = 0.,
    dataset_aug_prob = 0.,
    use_manual_seed = 0, # -1 for no seed
    debug_and_crash_mode = True
):
    model = Trainer(
        name,
        results_dir,
        models_dir,
        batch_size = batch_size,
        gradient_accumulate_every = gradient_accumulate_every,
        image_size = image_size,
        network_capacity = network_capacity,
        transparent = transparent,
        lr = learning_rate,
        num_workers = num_workers,
        save_every = save_every,
        trunc_psi = trunc_psi,
        fp16 = fp16,
        cl_reg = cl_reg,
        fq_layers = fq_layers,
        fq_dict_size = fq_dict_size,
        attn_layers = attn_layers,
        no_const = no_const,
        aug_prob = aug_prob,
        dataset_aug_prob = dataset_aug_prob,
        use_manual_seed = use_manual_seed,
        debug_and_crash_mode = debug_and_crash_mode
    )

    if not new:
        model.load(load_from)
    else:
        model.clear()

    if generate:
        now = datetime.now()
        timestamp = now.strftime("%m-%d-%Y_%H-%M-%S")
        samples_name = f'generated-{timestamp}'
        model.evaluate(samples_name, num_image_tiles)
        print(f'sample images generated at {results_dir}/{name}/{samples_name}')
        return

    if generate_interpolation:
        now = datetime.now()
        timestamp = now.strftime("%m-%d-%Y_%H-%M-%S")
        samples_name = f'generated-{timestamp}'
        model.generate_interpolation(samples_name, num_image_tiles, save_frames = save_frames)
        print(f'interpolation generated at {results_dir}/{name}/{samples_name}')
        return

    model.set_data_src(data)

    for _ in tqdm(range(num_train_steps - model.steps), mininterval=10., desc=f'{name}<{data}>'):
        retry_call(model.train, tries=3, exceptions=NanException)
        if _ % 50 == 0:
            model.print_log()

if __name__ == "__main__":
    fire.Fire(train_from_folder)
