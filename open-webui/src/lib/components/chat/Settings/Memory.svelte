<script lang="ts">
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import localizedFormat from 'dayjs/plugin/localizedFormat';
	import { getContext, onMount } from 'svelte';

	import { deleteMemoriesByUserId, deleteMemoryById, getMemories } from '$lib/apis/memories';
	import AddMemoryModal from './Personalization/AddMemoryModal.svelte';
	import EditMemoryModal from './Personalization/EditMemoryModal.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

	const i18n = getContext('i18n');
	dayjs.extend(localizedFormat);

	let memories = [];
	let loading = true;

	let showAddMemoryModal = false;
	let showEditMemoryModal = false;
	let selectedMemory = null;
	let showClearConfirmDialog = false;

	const loadMemories = async () => {
		memories = await getMemories(localStorage.token);
		loading = false;
	};

	const onClearConfirmed = async () => {
		const res = await deleteMemoriesByUserId(localStorage.token).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res && memories.length > 0) {
			toast.success($i18n.t('Memory cleared successfully'));
			memories = [];
		}
		showClearConfirmDialog = false;
	};

	onMount(() => {
		loadMemories();
	});
</script>

<AddMemoryModal
	bind:show={showAddMemoryModal}
	on:save={async () => {
		memories = await getMemories(localStorage.token);
	}}
/>

<EditMemoryModal
	bind:show={showEditMemoryModal}
	memory={selectedMemory}
	on:save={async () => {
		memories = await getMemories(localStorage.token);
	}}
/>

<ConfirmDialog
	title={$i18n.t('Clear Memory')}
	message={$i18n.t('Are you sure you want to clear all memories? This action cannot be undone.')}
	show={showClearConfirmDialog}
	on:confirm={onClearConfirmed}
	on:cancel={() => {
		showClearConfirmDialog = false;
	}}
/>

<div
	id="tab-memory"
	class="flex flex-col h-full justify-between text-sm"
>
	<div class="py-1 overflow-y-scroll max-h-[28rem] md:max-h-full flex-1">
		<div class="flex items-center justify-between mb-3">
			<div class="text-sm font-medium">
				{$i18n.t('Memory')}
			</div>
			<div class="flex gap-1.5">
				<button
					class="px-3 py-1.5 text-xs font-medium hover:bg-black/5 dark:hover:bg-white/5 outline outline-1 outline-gray-300 dark:outline-gray-800 rounded-3xl"
					on:click={() => {
						showAddMemoryModal = true;
					}}
				>
					{$i18n.t('Add Memory')}
				</button>
				<button
					class="px-3 py-1.5 text-xs font-medium text-red-500 hover:bg-black/5 dark:hover:bg-white/5 outline outline-1 outline-red-100 dark:outline-red-800 rounded-3xl"
					on:click={() => {
						if (memories.length > 0) {
							showClearConfirmDialog = true;
						} else {
							toast.error($i18n.t('No memories to clear'));
						}
					}}
				>
					{$i18n.t('Clear memory')}
				</button>
			</div>
		</div>

		{#if loading}
			<div class="text-center text-gray-500 py-10">
				{$i18n.t('Loading...')}
			</div>
		{:else if memories.length > 0}
			<div class="text-left text-sm w-full overflow-y-auto">
				<div class="relative overflow-x-auto">
					<table class="w-full text-sm text-left text-gray-600 dark:text-gray-400 table-auto">
						<thead
							class="text-xs text-gray-700 uppercase bg-transparent dark:text-gray-200 border-b-2 border-gray-50 dark:border-gray-850/30"
						>
							<tr>
								<th scope="col" class="px-3 py-2">{$i18n.t('Name')}</th>
								<th scope="col" class="px-3 py-2 hidden md:flex">{$i18n.t('Last Modified')}</th>
								<th scope="col" class="px-3 py-2 text-right" />
							</tr>
						</thead>
						<tbody>
							{#each memories as memory}
								<tr class="border-b border-gray-50 dark:border-gray-850/30 items-center">
									<td class="px-3 py-1">
										<div class="line-clamp-1">
											{memory.content}
										</div>
									</td>
									<td class="px-3 py-1 hidden md:flex h-[2.5rem]">
										<div class="my-auto whitespace-nowrap">
											{dayjs(memory.updated_at * 1000).format('LLL')}
										</div>
									</td>
									<td class="px-3 py-1">
										<div class="flex justify-end w-full">
											<Tooltip content="Edit">
												<button
													class="self-center w-fit text-sm px-2 py-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
													on:click={() => {
														selectedMemory = memory;
														showEditMemoryModal = true;
													}}
												>
													<svg
														xmlns="http://www.w3.org/2000/svg"
														fill="none"
														viewBox="0 0 24 24"
														stroke-width="1.5"
														stroke="currentColor"
														class="w-4 h-4"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125"
														/>
													</svg>
												</button>
											</Tooltip>

											<Tooltip content="Delete">
												<button
													class="self-center w-fit text-sm px-2 py-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
													on:click={async () => {
														const res = await deleteMemoryById(
															localStorage.token,
															memory.id
														).catch((error) => {
															toast.error(`${error}`);
															return null;
														});

														if (res) {
															toast.success($i18n.t('Memory deleted successfully'));
															memories = await getMemories(localStorage.token);
														}
													}}
												>
													<svg
														xmlns="http://www.w3.org/2000/svg"
														fill="none"
														viewBox="0 0 24 24"
														stroke-width="1.5"
														stroke="currentColor"
														class="w-4 h-4"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
														/>
													</svg>
												</button>
											</Tooltip>
										</div>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		{:else}
			<div class="text-center flex h-full text-sm w-full">
				<div class="my-auto pb-10 px-4 w-full text-gray-500">
					{$i18n.t('Memories accessible by LLMs will be shown here.')}
				</div>
			</div>
		{/if}
	</div>
</div>
