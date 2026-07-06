<template>
  <form class="instrument-form" @submit.prevent="handleSubmit">
    <div class="form-group">
      <label>仪器名称 <span class="required">*</span></label>
      <input v-model="form.name" required placeholder="请输入仪器名称" />
    </div>

    <div class="form-row">
      <div class="form-group">
        <label>位置</label>
        <input v-model="form.location" placeholder="如：A栋301" />
      </div>
      <div class="form-group">
        <label>每小时价格（元）</label>
        <input v-model.number="form.price_per_hour" type="number" step="0.01" min="0" placeholder="选填" />
      </div>
    </div>

    <div class="form-group">
      <label>描述</label>
      <textarea v-model="form.description" placeholder="仪器描述" rows="3" />
    </div>

    <div v-if="isEdit" class="form-group">
      <label>状态</label>
      <select v-model="form.status">
        <option value="available">可用</option>
        <option value="maintenance">维护中</option>
        <option value="retired">已报废</option>
      </select>
    </div>

    <div class="form-row">
      <div class="form-group form-checkbox">
        <label>
          <input v-model="form.requires_approval" type="checkbox" />
          预约需要管理员审批
        </label>
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label>最少提前预约（分钟）</label>
        <input v-model.number="form.min_notice_minutes" type="number" min="0" />
      </div>
      <div class="form-group">
        <label>预约间隔缓冲（分钟）</label>
        <input v-model.number="form.cleanup_time_minutes" type="number" min="0" />
      </div>
    </div>

    <div class="form-group">
      <label>图片</label>
      <div class="image-upload">
        <div v-if="imagePreview" class="image-preview">
          <img :src="imagePreview" alt="图片预览" />
          <button type="button" class="btn-remove-image" @click="removeImage">删除</button>
        </div>
        <input type="file" accept="image/*" @change="onImageSelect" />
      </div>
    </div>

    <div v-if="isEdit" class="form-group">
      <label>附件管理</label>
      <div class="attachment-upload">
        <input type="file" @change="onFileSelect" />
        <button type="button" class="btn-upload" :disabled="!selectedFile" @click="uploadFile">
          {{ uploading ? '上传中...' : '上传' }}
        </button>
      </div>
      <ul v-if="attachments.length > 0" class="attachment-list">
        <li v-for="att in attachments" :key="att.id">
          <a :href="`/api/v1/instruments/${instrumentId}/attachments/${att.id}`" target="_blank">
            {{ att.original_filename }}
          </a>
          <span class="file-size">({{ (att.file_size / 1024).toFixed(1) }} KB)</span>
          <button type="button" class="btn-del" @click="removeFile(att.id)">删除</button>
        </li>
      </ul>
      <p v-else class="no-files">暂无附件</p>
    </div>

    <ErrorAlert :message="error" />

    <div class="form-actions">
      <button type="button" class="btn-cancel" @click="$router.back()">取消</button>
      <button type="submit" class="btn-primary" :disabled="saving">
        {{ saving ? '保存中...' : '保存' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { createInstrument, updateInstrument, getAttachments, deleteAttachment, uploadAttachment, uploadImage, deleteImage, type AttachmentInfo } from '../../api/instruments'
import ErrorAlert from '../common/ErrorAlert.vue'

const props = defineProps<{
  instrumentId?: string
  initial?: any
}>()

const emit = defineEmits<{ saved: [] }>()

const isEdit = !!props.instrumentId
const saving = ref(false)
const uploading = ref(false)
const error = ref<string | null>(null)
const selectedFile = ref<File | null>(null)
const selectedImage = ref<File | null>(null)
const imagePreview = ref<string | null>(null)
const attachments = ref<AttachmentInfo[]>([])

const form = reactive({
  name: '',
  location: '',
  description: '',
  status: 'available',
  requires_approval: true,
  price_per_hour: null as number | null,
  min_notice_minutes: 60,
  cleanup_time_minutes: 15,
})

onMounted(async () => {
  if (props.initial) {
    Object.assign(form, props.initial)
    if (props.initial.image_url) {
      imagePreview.value = props.initial.image_url
    }
  }
  if (props.instrumentId) {
    try {
      attachments.value = await getAttachments(props.instrumentId)
    } catch {}
  }
})

function onImageSelect(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    selectedImage.value = file
    imagePreview.value = URL.createObjectURL(file)
  }
}

async function removeImage() {
  selectedImage.value = null
  imagePreview.value = null
  if (props.instrumentId) {
    try {
      await deleteImage(props.instrumentId)
    } catch {}
  }
}

function onFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  selectedFile.value = target.files?.[0] || null
}

async function uploadFile() {
  if (!selectedFile.value || !props.instrumentId) return
  uploading.value = true
  try {
    await uploadAttachment(props.instrumentId, selectedFile.value)
    attachments.value = await getAttachments(props.instrumentId)
    selectedFile.value = null
  } catch {
    error.value = '上传失败'
  } finally {
    uploading.value = false
  }
}

async function removeFile(attachmentId: string) {
  if (!props.instrumentId) return
  try {
    await deleteAttachment(props.instrumentId, attachmentId)
    attachments.value = attachments.value.filter((a) => a.id !== attachmentId)
  } catch {
    error.value = '删除失败'
  }
}

async function handleSubmit() {
  saving.value = true
  error.value = null
  try {
    let id = props.instrumentId
    if (isEdit && id) {
      await updateInstrument(id, form)
    } else {
      const result = await createInstrument(form)
      id = result.id
    }
    if (selectedImage.value && id) {
      await uploadImage(id, selectedImage.value)
    }
    emit('saved')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.instrument-form {
  max-width: 600px;
}
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  font-size: 14px;
  color: #374151;
  margin-bottom: 6px;
  font-weight: 500;
}
.required { color: #dc2626; }
.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-group textarea { resize: vertical; }
.form-row {
  display: flex;
  gap: 12px;
}
.form-row .form-group {
  flex: 1;
}
.form-checkbox label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.form-checkbox input {
  width: auto;
}
.image-upload {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.image-preview {
  display: flex;
  align-items: center;
  gap: 12px;
}
.image-preview img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.btn-remove-image {
  padding: 4px 12px;
  border: 1px solid #fecaca;
  color: #dc2626;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.attachment-upload {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}
.btn-upload {
  padding: 6px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}
.btn-upload:disabled { opacity: 0.6; }
.attachment-list {
  list-style: none;
  padding: 0;
}
.attachment-list li {
  font-size: 14px;
  padding: 4px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.attachment-list a { color: #3b82f6; text-decoration: none; }
.file-size { color: #94a3b8; font-size: 12px; }
.btn-del {
  margin-left: auto;
  background: none;
  border: none;
  color: #dc2626;
  cursor: pointer;
  font-size: 13px;
}
.no-files { font-size: 14px; color: #94a3b8; }
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
.btn-cancel {
  padding: 10px 24px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
}
.btn-primary {
  padding: 10px 24px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}
.btn-primary:disabled { opacity: 0.6; }
</style>
