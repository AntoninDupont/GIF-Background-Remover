__all__ = ['gif_remove_background']


from PIL import Image 
import os
import glob
import requests


def _extract_frames(input_file, output_folder='tmp'):
    frame = Image.open(input_file)
    nframes = 0
    if output_folder not in os.listdir(): os.mkdir(output_folder)
    while frame:
        frame.save('{}/{}.png'.format(output_folder, nframes), 'PNG')
        nframes += 1
        try: frame.seek(nframes)
        except EOFError: break
    return frame.info['duration']


def _remove_background(images_path='tmp', output_folder='tmp', api_key='SywF4y5eU8mGr72purDXxgHV'):
    for img in os.listdir(images_path):
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': open('{}/{}'.format(images_path, img), 'rb')},
            data={'size': 'auto'},
            headers={'X-Api-Key': api_key},
        )
        if output_folder not in os.listdir(): os.mkdir(output_folder)
        if response.status_code == requests.codes.ok:
            with open('{}/{}'.format(output_folder, img), 'wb') as out: out.write(response.content)
        else:
            print("Error:", response.status_code, response.text)
            break


def _merge_frames(output_file, duration, intput_folder='tmp'):
    image_list = []
    for filename in sorted(glob.glob('{}/*.png'.format(intput_folder))):
        im=Image.open(filename)
        image_list.append(im)
    image_list[0].save("{}.gif".format(output_file), save_all=True, append_images=image_list[1:], optimize=False, duration=duration, loop=0, disposal=2)
    for img in os.listdir():
        os.remove(img)
    os.removedirs(intput_folder)


def gif_remove_background(input_file, api_key, output_file=None):
    duration = _extract_frames(input_file)
    _remove_background(api_key=api_key)
    _merge_frames(input_file[:-4] + '_no_bg.gif', duration)


if __name__ == '__main__':
    print('GIF Background Remover')
    api_key = None
    while True:
        print('   0. Quit\n   1. Set API key' + (api_key != None) * '\n   2. Transform a GIF')
        user_input = input()
        if user_input not in ['0', '1'] and not api_key: print('\nInput is not valid. Try again:')
        elif user_input not in ['0', '1', '2'] and api_key: print('\nInput is not valid. Try again:')
        elif user_input == '0': break
        elif user_input == '1':
            print('Enter API key (could be obtained on https://www.remove.bg):')
            api_key = input()
            print(api_key)
        elif user_input == '2':
            print('Enter input file path:')
            try:
                path = input()
                if path[-4:] != '.gif':
                    print('ValueError: GIF file expected, got {} instead'.format(path[-3:]))
                    continue
                file_name = path.split('/')[-1][:-4]
                gif_remove_background(path, file_name + '_no_bg')
                print('Done!')
            except:
                print('\nValueError: file not found. Try again:')
