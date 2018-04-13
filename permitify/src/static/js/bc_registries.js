/* global FORM_HANDLERS, $ */

FORM_HANDLERS['incorporation.bc_registries'] = function (form, response) {
  console.log('here')
  if (response.success === true) {
    $(form).find('.legal-entity-id').remove()
    $(form).append(
      `
      <div class="legal-entity-id">
      Your legal entity id is:
      <code>${response.result.claim.legal_entity_id[0]}</code>
      </div>

      `
    )
  }
}
