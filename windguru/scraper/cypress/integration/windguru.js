const zip = (a, b) => a.map((k, i) => [k, b[i]]);
const year = new Date().getFullYear()
const month = new Date().getMonth()+1

describe('scrap windguru', () => {
  beforeEach(() => {
    cy.visit('https://www.windguru.cz/261')
  })
  it('should get first forecast', () => {
    cy.get('#tabid_0_0_dates').children('td').then((dates) => {
      cy.get('#tabid_0_0_TMP').children('td').then((temp) => {
        cy.request('POST', 'http://localhost:8000/save', Object.fromEntries(zip(
          Array.prototype.slice.call(dates).map((date) => {
            const d = date.innerText
            const [_, dom, hour] = d.match(/.{2}\s*([0-9]{2})\.\s*([0-9]{2})h/)
            return new Date(year, month, dom, hour, 0, 0).toISOString()
          }),
          Array.prototype.slice.call(temp).map((t) => parseInt(t.innerText))
        )))
      })
    })
  })
})
