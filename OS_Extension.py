import os


def delete_files_in_dir(idp, ext=None, filter_str=None, sort_result=True, recursive=False):

    """ ext can be a list of extensions or a single extension
        (e.g. ['.jpg', '.png'] or '.jpg')
    """

    fps = get_file_paths_in_dir(
        idp,
        ext=ext,
        filter_str=filter_str,
        sort_result=sort_result,
        recursive=recursive)

    for fp in fps:
        assert os.path.isfile(fp)
        os.remove(fp)

def get_file_paths_in_dir(idp,
                          ext=None,
                          filter_str=None,
                          base_name_only=False,
                          without_ext=False,
                          sort_result=True,
                          recursive=False):

    """ ext can be a list of extensions or a single extension
        (e.g. ['.jpg', '.png'] or '.jpg')
    """

    if recursive:
        ifp_s = []
        for root, dirs, files in os.walk(idp):
            ifp_s += [os.path.join(root, ele) for ele in files]
    else:
        ifp_s = [os.path.join(idp, ele) for ele in os.listdir(idp)
                 if os.path.isfile(os.path.join(idp, ele))]

    if ext is not None:
        if isinstance(ext, list):
            ifp_s = [ifp for ifp in ifp_s if os.path.splitext(ifp)[1].lower() in ext]
        else:
            ifp_s = [ifp for ifp in ifp_s if os.path.splitext(ifp)[1].lower() == ext]

    if filter_str is not None:
        ifp_s = [ifp for ifp in ifp_s if filter_str in ifp]

    if base_name_only:
        ifp_s = [os.path.basename(ifp) for ifp in ifp_s]

    if without_ext:
        ifp_s = [os.path.splitext(ifp)[0] for ifp in ifp_s]

    if sort_result:
        ifp_s = sorted(ifp_s)

    return ifp_s


def get_image_file_paths_in_dir(idp,
                                base_name_only=False,
                                without_ext=False,
                                sort_result=True,
                                recursive=True):
    return get_file_paths_in_dir(
        idp,
        ext=['.jpg', '.png'],
        base_name_only=base_name_only,
        without_ext=without_ext,
        sort_result=sort_result,
        recursive=recursive)


def get_stem(ifp):
    return os.path.splitext(os.path.basename(ifp))[0]


def get_basename(ifp):
    return os.path.basename(ifp)


def mkdir_safely(odp):
    if not os.path.isdir(odp):
        os.mkdir(odp)


def makedirs_safely(odp):
    if not os.path.isdir(odp):
        os.makedirs(odp)


def ensure_trailing_slash(some_path):
    return os.path.join(some_path, '')


def get_first_valid_path(list_of_paths):
    first_valid_path=None
    for path in list_of_paths:
        if first_valid_path is None and (os.path.isdir(path) or os.path.isfile(path)):
            first_valid_path = path
    return first_valid_path


def get_folders_matching_scheme(path_to_image_folders, pattern):
    target_folder_paths = []
    for root, dirs, files in os.walk(path_to_image_folders):

        match_result = pattern.match(os.path.basename(root))

        if match_result:    # basename matched the pattern
            target_folder_paths.append(root)

        # if os.path.basename(root) == target_folder_name_scheme:
        #     print 'Found Target Folder: ' + str(root)
        #     target_folder_paths.append(root)
    return target_folder_paths


def get_most_specific_parent_dir(possible_parent_dirs, possible_sub_dir):

    #print 'possible_sub_dir'
    #print possible_sub_dir

    current_parent_dir = ''

    for possible_parent_dir in possible_parent_dirs:

        #print 'possible_parent_dir'
        #print possible_parent_dir

        if is_subdir(possible_parent_dir, possible_sub_dir):

            #print 'is sub dir'

            if current_parent_dir == '':
                current_parent_dir = possible_parent_dir
            else: # there is another parent dir already found

                result = is_subdir(current_parent_dir, possible_parent_dir)
                if result:
                    print('WARNING: FOUND A MORE SPECIFIC PARENT DIR')
                    print('current_parent_dir: ' + current_parent_dir)
                    print('possible_parent_dir' + possible_parent_dir)
                    current_parent_dir = possible_parent_dir

    return current_parent_dir


def is_subdir(possible_parent_dir, possible_sub_dir):
    possible_parent_dir = os.path.realpath(possible_parent_dir)
    possible_sub_dir = os.path.realpath(possible_sub_dir)

    return possible_sub_dir.startswith(possible_parent_dir + os.sep)