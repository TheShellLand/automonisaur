import os
import re
import time
import warnings
import datetime

from swiftclient.service import SwiftService

from automon.log import Logging
from automon.integrations.swift.error import SwiftError_
# from automon.integrations.swift.config import SwiftConfig
from automon.integrations.swift.iterables import SwiftList, SwiftItem

log = Logging(__name__, Logging.INFO)

Logging('requests', Logging.CRITICAL)
Logging('swiftclient', Logging.CRITICAL)


class SwiftClient:
    def __init__(self):
        self._log = Logging(SwiftClient.__name__, Logging.DEBUG)

    @staticmethod
    def list_summary(files, folders):
        return files, folders

    def list_container(self, container, summary=False, filter='',
                       separate=False) -> [SwiftItem]:

        self._log.info(f'listing {container} (filter: {filter})')

        swift_objects = []
        swift_objects_v2 = []
        files = []
        files_v2 = []
        folders = []
        folders_v2 = []

        for page in SwiftList(container).list_gen():

            for item in page.list_gen():
                item_v1 = item.data()
                item_v2 = item

                if filter:
                    if not item.filter(filter):
                        continue

                swift_objects.append(item_v1)
                swift_objects_v2.append(item_v2)

                if item.is_directory():
                    folders.append(item_v1)
                    folders_v2.append(item_v2)
                else:
                    files.append(item_v1)
                    files_v2.append(item_v2)

        self._log.debug(f'Listing for {container}: {len(swift_objects)} objects')

        if summary:
            return len(swift_objects)

        if separate:
            self.list_summary(files, folders)

        return swift_objects

    def cleanup(self, container, days=7):

        msg = (f'Starting cleanup \n'
               f'>Retention policy: {days} days \n')
        self._log.info(msg)

        today = datetime.date.today()
        start_time = time.time()

        # Delete backups older than 7 days
        cleanup = self.list_container(container)
        total = len(cleanup)
        pending_deletion = []
        dates_to_retrain = []

        # keep one week of data
        for day in range(days + 1):
            # '2020-04-01'
            keep = today - datetime.timedelta(days=day)
            dates_to_retrain.append(keep)

        progress = 0

        # create a list of items to delete
        for item in cleanup:

            progress += 1
            percent = format(progress / total * 100, '.2f')

            item_s = SwiftItem(item)
            name = item_s.name

            found = False
            # check if item name is within date range
            for date in dates_to_retrain:
                # '^2020-04-01'
                regex = f'^{date}'

                if re.search(regex, item_s.name):
                    self._log.info(f"{percent}% ({progress}/{total}) cleanup retain: \'{regex}\', {name}")
                    found = True
                    break

            if not found:
                pending_deletion.append(item)
                self._log.info(f"{percent}% ({progress}/{total}) pending deletion: {name}")

        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time / 60)

        msg = (f'>Created deletion list for past {days} days (Deleting: {len(pending_deletion)} objects)\n'
               f">Cleanup has been running for: {minutes} minutes")
        self._log.debug(msg)

        objects = 0
        folders = 0
        total = len(pending_deletion)
        progress = 0

        # create stats on what will be deleted
        for item in pending_deletion:
            item_s = SwiftItem(item)
            name = item_s.name

            progress += 1
            percent = format(progress / total * 100, '.2f')
            elapsed_time = time.time() - start_time
            minutes = int(elapsed_time / 60)

            if item_s.is_directory():
                folders += 1
            else:
                objects += 1

            self._log.info(f'{percent}% ({progress}/{total}) summarizing deletion: {name}')

        msg = (f'Cleaning up older than {days} days: \n'
               f'>{total} *total objects* \n'
               f'>{objects} *objects* \n'
               f'>{folders} *folders* \n'
               f'see debug messages')
        self._log.debug(msg)

        progress = 0

        # delete objects
        for item in pending_deletion:
            name = SwiftItem(item).name

            progress += 1
            percent = format(progress / total * 100, '.2f')
            elapsed_time = time.time() - start_time
            minutes = int(elapsed_time / 60)

            # this does the actual deletion
            self.delete_object(container, item)
            self._log.info(f'{percent}% ({progress}/{total}) deleted: {name}')

            if progress % 10000 == 0 or progress % total == 0:
                elapsed_time = time.time() - start_time
                minutes = int(elapsed_time / 60)

                msg = (f'>Deletion is currently at `{percent}%` ({progress}/{total})\n'
                       f">Backup has been running for: {minutes} minutes")
                self._log.debug(msg)

        if pending_deletion:
            msg = ('Cleanup Finished\n'
                   f">It took: {minutes} minutes")
            self._log.debug(msg)

    def backup(self, source, destination, test=None, skip_known=True):

        # TODO: for some reason it's finished time shows 3 minutes, when debug shows 90 minutes

        today = f'{datetime.date.today()}'
        start_time = time.time()
        progress = 0
        retries = 0

        msg = f'Backup {source} started'
        self._log.debug(msg)

        items = self.list_container(source)
        backups = self.list_container(destination, filter=today)
        total = len(items)

        source_stats = self.stats(source, show_types=True)

        for item in items:

            progress += 1

            s_item = SwiftItem(item)
            name = s_item.name

            if test:
                regex = str(test)
                if re.search(regex, item):
                    self._log.debug(f'Test match: {test} \n>{item}')

                else:
                    continue

            percent = format(progress / total * 100, '.2f')

            # skip items that are already backed up
            if skip_known:
                exists = False
                for b in backups:
                    b = SwiftItem(b)
                    if f'{today}/{s_item.name}' == b.name:
                        self._log.info(f'{percent}% ({progress}/{total}) exists, skipping {s_item.name}')
                        exists = True
                        break
                if exists:
                    continue

            if progress % 10000 == 0 or progress % total == 0:
                elapsed_time = time.time() - start_time
                minutes = int(elapsed_time / 60)
                msg = (f'>Backup {source} is currently at `{percent}%` ({progress}/{total})\n'
                       f">Backup has been running for: {minutes} minutes")
                self._log.debug(msg)

                self.stats(destination, filter=today)

            retry = True
            while True:
                with SwiftService() as swift:
                    try:
                        if s_item.is_directory():

                            folder = f'{today}/{name}'
                            os.makedirs(folder, exist_ok=True)
                            compatible_name = os.path.split(name)[0]

                            options = {"destination": f"/{destination}/{today}/{compatible_name}"}

                            try:
                                for i in swift.upload(destination, [folder], options):

                                    if i["success"]:
                                        self._log.info(
                                            f'{percent}% ({progress}/{total}) '
                                            f'created directory /{destination}/{today}/{name}')

                                        retry = False

                                    if "error" in i and isinstance(i["error"], Exception):
                                        self._log.error(f'{SwiftError_(i)}')

                                        retries += 1

                            except Exception as _:
                                self._log.error(item)

                                retries += 1

                            # TODO: find a thread-safe method to delete folders
                            # shutil.rmtree(str(today))

                        else:

                            options = {"destination": f"/{destination}/{today}/{name}"}

                            for i in swift.copy(source, [name], options):

                                if test:
                                    retry = False

                                if i["success"]:
                                    if i["action"] == "copy_object":
                                        self._log.info(
                                            f'{percent}% ({progress}/{total}) '
                                            f'copied {i["destination"]} from /{i["container"]}/{i["object"]}')

                                    if i["action"] == "create_container":
                                        self._log.info(
                                            f'{percent}% ({progress}/{total}) '
                                            f'container {i["container"]} created')

                                    retry = False

                                else:
                                    if "error" in i and isinstance(i["error"], Exception):

                                        if 'Authorization Failure. Authorization failed' in str(i):
                                            error = (
                                                f'''This error happens every once in a while. I'm not really sure why, 
                                                but might be some kind of stale timeout when SwiftService() isn't doing 
                                                anything \n'''
                                                f'{SwiftError_(i)}'
                                            )
                                        else:
                                            error = f'{SwiftError_(i)}'

                                        log.error(error)
                                        retries += 1

                    except Exception as _:
                        log.error(item)
                        retries += 1

                if not retry:
                    break

        self._log.info('building backup summary')

        source_total_objects, \
        source_total_dirs, \
        source_objects, _, _ = source_stats

        filter_destination_total_objects, \
        filter_destination_total_dirs, \
        filter_objects, _, _ = self.stats(destination, post_log=True, filter=today)

        destination_total_objects, \
        destination_total_dirs, \
        destination_objects, _, _ = self.stats(destination, post_log=False)

        # elapsed_time = time.time() - start_time
        # minutes = int(elapsed_time / 60)

        msg = (
            f'*Backup Finished* \n'
            f'Stats for {source}: \n'
            f'>{source_total_objects} *total objects* \n'
            f'>{source_objects} *objects* \n'
            f'>{source_total_dirs} *dirs* \n'
            f'Stats for {destination} ({today}): \n'
            f'>{filter_destination_total_objects} *total objects* \n'
            f'>{filter_objects} *objects* \n'
            f'>{filter_destination_total_dirs} *dirs* \n'
            f'Stats for all {destination}: \n'
            f'>{destination_total_objects} *total objects* \n'
            f'>{destination_objects} *objects* \n'
            f'>{destination_total_dirs} *dirs* \n')
        log.debug(msg)

        # TODO: new files may be added during the backup, so need verify only the initial files being backed up

        # missing = self.find_missing(source, destination, filter=today, post_log=False)
        # missing_count = len(missing)
        # if missing:
        #     try:
        #         self.log.info(
        #             f'Missing {missing_count} objects'
        #             '>'.join(missing)
        #         )
        #     except Exception as e:
        #         # debug testing
        #         slacklog.error(f'{e}')
        # else:
        #     slacklog.info(msg)
        #
        #     msg = ('*Backup Finished* \n'
        #            f'>It took: {minutes} minutes ({retries} retries)\n')
        #     self.log.debug(msg)

    def find_missing(self, source, destination, filter, post_log=True):

        msg = f'Verifying backup {destination} {filter} \n'

        missing_objects = ()
        missing_objects_list = []

        today = datetime.date.today()

        src_list = self.list_container(source)
        dst_list = self.list_container(destination, filter=filter)

        total = len(src_list)

        progress = 0

        for a_item in src_list:

            a_name = SwiftItem(a_item).name

            progress += 1
            percent = format(progress / total * 100, '.2f')

            found = False
            for b_item in dst_list:
                b_name = SwiftItem(b_item).name
                if f'{today}/{a_name}' == b_name:
                    found = True
                    break
            if not found:
                self._log.info(f'{percent}% ({progress}/{total}) backup missing: {a_name}')
                missing_objects + (tuple(f' * {a_item} \n'))
                missing_objects_list.append(a_item)
            else:
                self._log.info(f'{percent}% ({progress}/{total}) verified, {a_name}')

        log.debug(f'missing_objects: {len(missing_objects)}')

        if missing_objects:
            msg = (f'Missing {len(missing_objects)} objects: \n'
                   '>List of missing: \n'
                   ''.join(missing_objects))

        return missing_objects_list

    def stats(self, container, filter='', post_log=True, show_types=False):

        self._log.info(f'stat {container} (filter: {filter})')

        list_items = self.list_container(container, filter=filter)
        total_dirs = 0
        list_types = {}

        for item in list_items:

            s_item = SwiftItem(item)

            key = s_item.content_type
            if key in list_types.keys():
                list_types[key] += 1
            else:
                list_types[key] = 1

            if s_item.is_directory():
                total_dirs += 1

        list_types = {k: v for k, v in sorted(list_types.items(), key=lambda item: item[1], reverse=True)}

        total_objects = len(list_items)
        objects = total_objects - total_dirs

        msg = ((f'Stats for {container}: \n'
                f'>{total_objects}*total objects* \n'
                f'>{objects}*objects* \n'
                f'>{total_dirs}*dirs* \n'))

        if filter:
            msg = ((f'Stats for {container} ({filter}): \n'
                    f'>{total_objects}*total objects* \n'
                    f'>{objects}*objects* \n'
                    f'>{total_dirs}*dirs* \n'))

        if show_types:
            msg = msg + f'>*types:* `{list_types}` \n'

        return total_objects, total_dirs, objects, list_items, list_types

    def delete_object(self, container, item):

        name = SwiftItem(item).name

        with SwiftService() as swift:
            try:
                for i in swift.delete(container=container, objects=[name]):
                    if i['success']:
                        self._log.info(f'deleted: {name}')

            except Exception as e:
                log.error(f'{e}')

    def delete(self, container, filter):

        deletion = self.list_container(container, filter=filter)

        deletion_count = len(deletion)
        progress = 0

        for item in deletion:

            name = SwiftItem(item).name

            progress += 1
            percent = format(progress / deletion_count * 100, '.2f')

            with SwiftService() as swift:
                try:
                    for i in swift.delete(container=container, objects=[name]):
                        if i['success']:
                            self._log.info(f'{percent}% ({progress}/{deletion_count}) deleted: {name}')

                except Exception as e:
                    log.error(f'{e}')

        log.debug(
            f'Deletion summary: \n>container: {container} \n>filter: {filter} \n>{deletion_count} objects deleted')

    def delete_container(self, container):

        with SwiftService() as swift:
            try:

                for _ in swift.delete(container):
                    self._log.info(f'deleting container: {container}')

            except Exception as e:
                log.error(f'{e}')

    def restore(self):
        return warnings.warn(NotImplemented)
